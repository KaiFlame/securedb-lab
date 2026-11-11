"""Desktop entry point: start real local databases/API and serve the built UI.

No Docker or Node process is required to open an already built installation.
All paths are resolved from this project; only OS Python prerequisites are external.
"""
import argparse
import functools
import hashlib
import http.client
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import threading
import time
import urllib.parse
import urllib.request
import webbrowser

ROOT=Path(__file__).resolve().parents[1]
STATE_DIR=ROOT/'.local/desktop'
ROOT_ID=hashlib.sha256(str(ROOT).lower().encode()).hexdigest()[:16]
URL='http://127.0.0.1:5173'
API_PORT=8000
FRONT_PORT=5173
STOP_FILE=STATE_DIR/'stop.request'
STATE_FILE=STATE_DIR/'state.json'
HIDDEN=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0
IS_WINDOWS=os.name=='nt'
_HOP={'connection','transfer-encoding','keep-alive','proxy-authenticate','proxy-authorization','te','trailers','upgrade','server','date'}

def project_path(relative):
    result=(ROOT/relative).resolve()
    if not result.is_relative_to(ROOT.resolve()):raise ValueError('Caminho fora da pasta do projeto.')
    return result

def tool_paths():
    return {'pg':project_path('.local/tools/postgres/bin'),
            'mongo':project_path('.local/tools/mongodb/bin/mongod.exe'),
            'mongo_tools':project_path('.local/tools/mongodb-tools/bin')}

def python_console():
    path=Path(sys.executable)
    return str(path.with_name('python.exe') if path.name.lower()=='pythonw.exe' else path)

def runtime_env():
    paths=tool_paths()
    env={**os.environ,'PYTHONUTF8':'1','PYTHONUNBUFFERED':'1',
         'LAB_RUNTIME':str(ROOT/'.local/runtime.json'),
         'LAB_ADMIN':str(ROOT/'.local/admin.json'),
         'LAB_BACKUPS':str(ROOT/'.local/backups'),
         'LAB_AUDIT':str(ROOT/'.local/audit/events.jsonl'),
         'LAB_EVIDENCE':str(ROOT/'evidencias')}
    env['PATH']=os.pathsep.join([str(paths['pg']),str(paths['mongo_tools']),str(paths['mongo'].parent),env.get('PATH','')])
    return env

def json_url(url):
    with urllib.request.urlopen(url,timeout=2) as response:
        return json.load(response)

def listening(port):
    with socket.socket() as sock:
        sock.settimeout(.3)
        return sock.connect_ex(('127.0.0.1',port))==0

def write_state(status,**extra):
    STATE_DIR.mkdir(parents=True,exist_ok=True)
    state={'root_id':ROOT_ID,'root':str(ROOT),'launcher_pid':os.getpid(),'status':status,
           'url':URL,'timestamp':time.time(),**extra}
    temporary=STATE_FILE.with_suffix('.tmp')
    temporary.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
    temporary.replace(STATE_FILE)

def verify_existing_databases():
    # Reject a service belonging to the former checkout or to another installation.
    from seed import pg_admin,mongo_admin
    if listening(55432):
        try:
            with pg_admin('postgres') as conn:
                actual=Path(conn.execute('SHOW data_directory').fetchone()[0]).resolve()
            if actual!=project_path('.local/native/pgdata'):raise ValueError()
        except Exception:raise RuntimeError('A porta 55432 está ocupada por outro ambiente. Encerre-o antes de continuar.') from None
    if listening(57017):
        try:
            client=mongo_admin()
            actual=Path(client.admin.command('getCmdLineOpts')['parsed']['storage']['dbPath']).resolve()
            client.close()
            if actual!=project_path('.local/native/mongodata'):raise ValueError()
        except Exception:raise RuntimeError('A porta 57017 está ocupada por outro ambiente. Encerre-o antes de continuar.') from None

class LocalHandler(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass  # Query strings and payloads never enter access logs.

    def list_directory(self,path):
        self.send_error(403,'Listagem de diretório desabilitada.')
        return None

    def end_headers(self):
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('X-Frame-Options','DENY')
        self.send_header('Referrer-Policy','no-referrer')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'")
        super().end_headers()

    def _api(self):
        length=self.headers.get('Content-Length','0')
        if not length.isdecimal() or int(length)>16384 or self.headers.get('Transfer-Encoding'):
            self.send_error(413,'Solicitação excede o limite permitido.');return
        body=self.rfile.read(int(length)) if int(length) else None
        headers={k:v for k,v in self.headers.items() if k.lower() not in _HOP|{'host','content-length'}}
        headers['Host']='127.0.0.1'
        conn=http.client.HTTPConnection('127.0.0.1',API_PORT,timeout=20)
        try:
            conn.request(self.command,self.path,body=body,headers=headers)
            response=conn.getresponse()
            data=response.read()
            self.send_response(response.status)
            for k,v in response.getheaders():
                if k.lower() not in _HOP|{'content-length'}:self.send_header(k,v)
            self.send_header('Content-Length',str(len(data)))
            self.end_headers()
            if self.command!='HEAD':self.wfile.write(data)
        except (OSError,http.client.HTTPException):
            self.send_error(503,'API local indisponível.')
        finally:conn.close()

    def do_GET(self):
        if self.path.split('?',1)[0]=='/desktop-health':
            data=json.dumps({'service':'SecureDB Lab desktop','root_id':ROOT_ID,'profile':'native'}).encode()
            self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
        elif self.path.startswith('/api/'):self._api()
        else:super().do_GET()

    def do_HEAD(self):
        if self.path.startswith('/api/'):self._api()
        else:super().do_HEAD()

    def _write(self):
        if self.path.startswith('/api/'):self._api()
        else:self.send_error(405)
    do_POST=_write
    do_PUT=_write
    do_PATCH=_write
    do_DELETE=_write

class DesktopRuntime:
    def __init__(self):
        self.api=None;self.server=None;self.database_started=False;self.log=None

    def start(self,progress=lambda text:None):
        paths=tool_paths()
        for path in [paths['pg']/'pg_ctl.exe',paths['mongo'],ROOT/'web/dist/index.html']:
            if not path.is_file():raise RuntimeError('Instalação incompleta: falta '+str(path.relative_to(ROOT)))
        if listening(FRONT_PORT) or listening(API_PORT):raise RuntimeError('As portas 5173/8000 já estão em uso. Não foi encerrado nenhum processo externo.')
        STATE_DIR.mkdir(parents=True,exist_ok=True)
        self.log=(STATE_DIR/'startup.log').open('ab')
        write_state('starting')
        # setup regenerates only path-dependent runtime files; it preserves keys/data.
        subprocess.run([python_console(),'scripts/lab.py','setup'],cwd=ROOT,env=runtime_env(),stdout=self.log,stderr=self.log,check=True,creationflags=HIDDEN)
        verify_existing_databases()
        progress('Iniciando bancos locais com TLS…')
        self.database_started=True
        init=subprocess.run([python_console(),'scripts/native.py','start','--pg-bin',str(paths['pg']),'--mongod',str(paths['mongo'])],cwd=ROOT,env=runtime_env(),stdout=self.log,stderr=self.log,creationflags=HIDDEN,timeout=120)
        if init.returncode:raise RuntimeError('A inicialização dos bancos falhou. Consulte .local/desktop/startup.log.')
        self.database_started=True
        progress('Iniciando API e verificando os serviços…')
        self.api=subprocess.Popen([python_console(),'-m','uvicorn','api.main:app','--host','127.0.0.1','--port',str(API_PORT),'--no-access-log'],cwd=ROOT,env=runtime_env(),stdout=self.log,stderr=self.log,creationflags=HIDDEN)
        deadline=time.monotonic()+40
        while time.monotonic()<deadline:
            if self.api.poll() is not None:raise RuntimeError('A API não iniciou. Consulte o log local.')
            try:
                if json_url('http://127.0.0.1:8000/api/health').get('status')=='ready':break
            except Exception:time.sleep(.25)
        else:raise RuntimeError('A API não ficou pronta no prazo previsto.')
        handler=functools.partial(LocalHandler,directory=str(ROOT/'web/dist'))
        self.server=ThreadingHTTPServer(('127.0.0.1',FRONT_PORT),handler)
        self.server.daemon_threads=True
        threading.Thread(target=self.server.serve_forever,daemon=True).start()
        write_state('ready',api_pid=self.api.pid)
        progress('Pronto. Aplicativo disponível no navegador.')

    def stop(self):
        failures=[]
        try:
            if self.server:
                try:self.server.shutdown();self.server.server_close();self.server=None
                except Exception:failures.append('interface')
            if self.api and self.api.poll() is None:
                try:
                    self.api.terminate()
                    try:self.api.wait(timeout=8)
                    except subprocess.TimeoutExpired:self.api.kill();self.api.wait(timeout=5)
                    self.api=None
                except Exception:failures.append('API')
            if self.database_started:
                try:
                    paths=tool_paths()
                    result=subprocess.run([python_console(),'scripts/native.py','stop','--pg-bin',str(paths['pg']),'--mongod',str(paths['mongo'])],cwd=ROOT,env=runtime_env(),stdout=self.log,stderr=self.log,creationflags=HIDDEN,timeout=40)
                    if result.returncode:raise RuntimeError()
                    self.database_started=False
                except Exception:failures.append('bancos; verifique o log local')
        finally:
            write_state('stop_failed' if failures else 'stopped',pending=failures)
            if self.log:self.log.close();self.log=None
        if failures:raise RuntimeError('Encerramento incompleto: '+', '.join(failures))

def lock_instance():
    STATE_DIR.mkdir(parents=True,exist_ok=True)
    handle=(STATE_DIR/'instance.lock').open('a+b')
    handle.seek(0,2)
    if handle.tell()==0:handle.write(b'1');handle.flush()
    handle.seek(0)
    import msvcrt
    try:msvcrt.locking(handle.fileno(),msvcrt.LK_NBLCK,1)
    except OSError:handle.close();return None
    return handle

def existing_ours():
    try:return json_url(URL+'/desktop-health').get('root_id')==ROOT_ID
    except Exception:return False

def gui(runtime,no_browser):
    import tkinter as tk
    from tkinter import messagebox
    window=tk.Tk();window.title('SecureDB Lab');window.geometry('470x285');window.resizable(False,False);window.configure(bg='#fcfbf9')
    icon=ROOT/'assets/securedb.ico'
    if icon.exists():window.iconbitmap(str(icon))
    status=tk.StringVar(value='Preparando o laboratório…');ready=threading.Event();closing=threading.Event()
    tk.Label(window,text='securedb / lab',font=('Segoe UI',22,'bold'),bg='#fcfbf9',fg='#7f2626').pack(anchor='w',padx=28,pady=(23,8))
    tk.Label(window,text='FACAMP · Ambiente local',font=('Segoe UI',10),bg='#fcfbf9',fg='#676965').pack(anchor='w',padx=30)
    tk.Label(window,textvariable=status,wraplength=405,justify='left',font=('Segoe UI',10),bg='#fcfbf9',fg='#222426').pack(anchor='w',padx=30,pady=20)
    buttons=tk.Frame(window,bg='#fcfbf9');buttons.pack(padx=28,fill='x')
    open_button=tk.Button(buttons,text='Abrir aplicativo',state='disabled',command=lambda:webbrowser.open(URL),bg='#7f2626',fg='white',padx=13,pady=6,relief='flat');open_button.pack(side='left')
    tk.Button(buttons,text='Ver acessos locais',command=lambda:os.startfile(ROOT/'.local/ACESSO_LOCAL.txt'),padx=10,pady=6,relief='flat').pack(side='left',padx=9)
    tk.Button(buttons,text='Pasta do projeto',command=lambda:os.startfile(ROOT),padx=7,pady=6,relief='flat').pack(side='left')
    def finish():
        if closing.is_set():return
        closing.set();status.set('Encerrando serviços e preservando os dados…')
        def stop():
            try:ready.wait();runtime.stop()
            except Exception as exc:window.after(0,lambda text=str(exc):messagebox.showerror('SecureDB Lab',text))
            finally:window.after(0,window.destroy)
        threading.Thread(target=stop,daemon=True).start()
    tk.Button(window,text='Encerrar laboratório',command=finish,relief='flat',fg='#7f2626',bg='#fcfbf9').pack(anchor='e',padx=25,pady=18)
    def start():
        try:
            runtime.start(lambda message:window.after(0,lambda:status.set(message)))
            if not closing.is_set():
                window.after(0,lambda:open_button.configure(state='normal'))
                if not no_browser:webbrowser.open(URL)
        except Exception as exc:
            write_state('failed',message=str(exc));window.after(0,lambda text=str(exc):status.set(text))
        finally:ready.set()
    def poll():
        if STOP_FILE.exists():finish()
        elif not closing.is_set():window.after(400,poll)
    window.protocol('WM_DELETE_WINDOW',finish)
    threading.Thread(target=start,daemon=True).start();window.after(400,poll);window.mainloop()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('action',nargs='?',choices=['start','stop','status'],default='start')
    parser.add_argument('--headless',action='store_true')
    parser.add_argument('--no-browser',action='store_true')
    args=parser.parse_args()
    STATE_DIR.mkdir(parents=True,exist_ok=True)
    if args.action=='status':
        print(json.dumps({'ready':existing_ours(),'root':str(ROOT)},ensure_ascii=False));return
    if args.action=='stop':
        STOP_FILE.write_text('stop',encoding='ascii')
        deadline=time.monotonic()+200
        while time.monotonic()<deadline:
            state=json.loads(STATE_FILE.read_text(encoding='utf-8')) if STATE_FILE.exists() else {}
            if state.get('status')=='stopped':print('Laboratório encerrado.');return
            time.sleep(.3)
        raise RuntimeError('O encerramento não foi confirmado. Confira o painel e o log local.')
    if not IS_WINDOWS:raise RuntimeError('O atalho desktop é destinado ao Windows; use o Compose em outros sistemas.')
    lock=lock_instance()
    if lock is None:
        if existing_ours() and not args.no_browser:webbrowser.open(URL)
        return
    try:
        # Clear the previous run's stop marker before the GUI starts polling it.
        # Clearing it later in the worker races with the GUI's first 400 ms poll.
        STOP_FILE.unlink(missing_ok=True)
        write_state('starting')
        runtime=DesktopRuntime()
        if args.headless:
            try:
                runtime.start(print)
                if not args.no_browser:webbrowser.open(URL)
                while not STOP_FILE.exists():time.sleep(.3)
            finally:runtime.stop()
        else:gui(runtime,args.no_browser)
    finally:lock.close()

if __name__=='__main__':main()
