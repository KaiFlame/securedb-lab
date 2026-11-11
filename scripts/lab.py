"""Portable entry point. No destructive cleanup and no arbitrary shell execution."""
import argparse
import base64
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT=Path(os.environ.get('LAB_PROJECT_ROOT',Path(__file__).resolve().parents[1])).resolve()
sys.path.insert(0,str(ROOT))

def command(args, **kwargs):
    return subprocess.run(args,cwd=ROOT,check=True,**kwargs)

def write_json(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')

def configured_port():
    value=os.getenv('WEB_PORT')
    if value is None and (ROOT/'.env').exists():
        for line in (ROOT/'.env').read_text(encoding='utf-8').splitlines():
            if line.startswith('WEB_PORT='):
                value=line.split('=',1)[1].strip()
    port=int(value or '8080')
    if not 1024<=port<=65535:
        raise ValueError('WEB_PORT deve estar entre 1024 e 65535.')
    return port

def setup():
    from certificates import generate
    local=ROOT/'.local'
    local.mkdir(exist_ok=True)
    if os.name!='nt':local.chmod(0o700)
    for name in ['runtime','admin','audit','ops-audit','backups','checks']:
        (local/name).mkdir(exist_ok=True)
    secrets_path=local/'secrets.json'
    if secrets_path.exists():
        s=json.loads(secrets_path.read_text(encoding='utf-8'))
    else:
        s={key:secrets.token_urlsafe(32) for key in ['pg_admin_password','pg_app_password','pg_auth_password','mongo_admin_password','mongo_app_password']}
        s['accounts']=[{'username':username,'password':secrets.token_urlsafe(16),'role':role,'tenant':tenant} for username,role,tenant in [('aurora.editor','editor','A'),('vertice.editor','editor','B'),('aurora.leitor','viewer','A')]]
        write_json(secrets_path,s)
    generate(local/'certs')
    port=configured_port()
    if not 1024<=port<=65535:
        raise ValueError('WEB_PORT deve estar entre 1024 e 65535.')
    runtime={k:s[k] for k in ['pg_app_password','pg_auth_password','mongo_app_password']}
    runtime.update(pg_host='postgres',mongo_host='mongo',ca_file='/run/ca/ca.crt',allowed_origins=[f'http://localhost:{port}',f'http://127.0.0.1:{port}','http://localhost:5173','http://127.0.0.1:5173'],secure_cookie=False)
    write_json(local/'runtime/runtime.json',runtime)
    write_json(local/'runtime.json',{**runtime,'pg_host':'127.0.0.1','pg_port':55432,'mongo_host':'127.0.0.1','mongo_port':57017,'ca_file':str(local/'certs/client/ca.crt')})
    admin={**s,'pg_host':'postgres','pg_port':5432,'mongo_host':'mongo','mongo_port':27017,'ca_file':'/run/ca/ca.crt'}
    write_json(local/'admin/admin.json',admin)
    write_json(local/'admin.json',{**admin,'pg_host':'127.0.0.1','pg_port':55432,'mongo_host':'127.0.0.1','mongo_port':57017,'ca_file':str(local/'certs/client/ca.crt')})
    backup_key=local/'admin/backup.key'
    if not backup_key.exists(): backup_key.write_bytes(secrets.token_bytes(32))
    envmap={'POSTGRES_ADMIN_PASSWORD':'pg_admin_password','POSTGRES_APP_PASSWORD':'pg_app_password','POSTGRES_AUTH_PASSWORD':'pg_auth_password','MONGO_ADMIN_PASSWORD':'mongo_admin_password','MONGO_APP_PASSWORD':'mongo_app_password'}
    (ROOT/'.env').write_text('\n'.join(f'{env}={s[key]}' for env,key in envmap.items())+f'\nWEB_PORT={port}\n',encoding='utf-8')
    if os.name!='nt':
        secrets_path.chmod(0o600)
        (ROOT/'.env').chmod(0o600)
        for folder in ['admin','audit','ops-audit','backups','checks']:
            (local/folder).chmod(0o700)
        for folder in ['runtime','certs/client']:
            (local/folder).chmod(0o755)
        for public in ['runtime/runtime.json','certs/client/ca.crt']:
            (local/public).chmod(0o644)
        for private in ['runtime.json','admin.json','admin/admin.json','admin/backup.key']:
            (local/private).chmod(0o600)
    (local/'ACESSO_LOCAL.txt').write_text('Somente dados sintéticos. Não publicar este arquivo.\n'+ '\n'.join(f"{a['username']} | {a['password']} | empresa {a['tenant']} | {a['role']}" for a in s['accounts']),encoding='utf-8')
    if os.name!='nt': (local/'ACESSO_LOCAL.txt').chmod(0o600)
    for name in ['evidencias','evidencias/app','evidencias/sql','evidencias/nosql']:
        (ROOT/name).mkdir(parents=True,exist_ok=True)
    print('Configuração e certificados gerados/preservados. Credenciais: .local/ACESSO_LOCAL.txt')

def compose(*args):
    env=os.environ.copy()
    if os.name!='nt':
        env.update(LOCAL_UID=str(os.getuid()),LOCAL_GID=str(os.getgid()))
    return command(['docker','compose',*args],env=env)

def diagnose():
    config=json.loads(subprocess.check_output(['docker','compose','config','--format','json'],cwd=ROOT,text=True))
    observed=[]
    for service in ['postgres','mongo']:
        if config['services'][service].get('ports'): raise RuntimeError('Banco com porta publicada!')
        cid=subprocess.check_output(['docker','compose','ps','-q',service],cwd=ROOT,text=True).strip()
        if not cid: raise RuntimeError(f'{service}: contêiner ausente')
        ins=json.loads(subprocess.check_output(['docker','inspect',cid],text=True))[0]
        if ins['HostConfig'].get('PortBindings'): raise RuntimeError('Publicação de banco detectada!')
        if not ins['State']['Running']: raise RuntimeError('Contêiner parado')
        observed.append({'service':service,'image':ins['Config']['Image'],'running':True,'published_ports':[]})
    net_name=config['networks']['data']['name']
    net=json.loads(subprocess.check_output(['docker','network','inspect',net_name],text=True))[0]
    assert net['Internal'] is True
    item={'id':'ENV-01','controls':['SQL-01','NOSQL-01','NOSQL-05'],'result':'PASS','timestamp':datetime.now(timezone.utc).isoformat(),'objective':'Contêineres ativos, rede de dados interna, bancos sem portas publicadas','observed':observed,'internal_network':True}
    write_json(ROOT/'evidencias/environment.json',item)
    print('ENV-01 PASS: configuração efetiva de rede e contêineres conferida.')

def main():
    parser=argparse.ArgumentParser(description='SecureDB Lab - operações locais reproduzíveis')
    parser.add_argument('action',choices=['setup','up','stop','seed','test','backup','restore','report','diagnose','preflight'])
    parser.add_argument('--database',choices=['sql','nosql','both'],default='both')
    args=parser.parse_args()
    if args.action=='setup': setup()
    elif args.action=='up':
        if not (ROOT/'.env').exists(): setup()
        compose('up','-d','--build','--wait','--wait-timeout','300')
        diagnose()
        print(f'Aplicação: http://localhost:{configured_port()}')
    elif args.action=='stop': compose('down')  # Preserves both data volumes.
    elif args.action=='seed': compose('--profile','tools','run','--rm','--no-deps','ops','python','scripts/seed.py')
    elif args.action=='test':
        diagnose()
        compose('--profile','tools','run','--rm','ops','pytest','tests')
    elif args.action in {'backup','restore'}:
        # Both run an isolated, measured round trip; never restore over source.
        compose('--profile','tools','run','--rm','ops','python','scripts/backup_restore.py','--database',args.database)
    elif args.action=='report': command([sys.executable,'scripts/report.py'])
    elif args.action=='diagnose': diagnose()
    elif args.action=='preflight': command([sys.executable,'scripts/preflight.py'])

if __name__=='__main__': main()
