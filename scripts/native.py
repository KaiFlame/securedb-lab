"""Optional Windows fallback. Same application, real TLS databases, loopback only.
Does not certify Compose networking. All data remains under .local/native.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.request
import socket

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'scripts'))

def spawn(args,log_path,env=None):
    log_path.parent.mkdir(parents=True,exist_ok=True)
    log=open(log_path,'ab')
    return subprocess.Popen(args,cwd=ROOT,stdout=log,stderr=log,env=env,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)

def wait(fn,seconds=45):
    deadline=time.monotonic()+seconds
    while time.monotonic()<deadline:
        try:
            result=fn()
            if result: return result
        except Exception: pass
        time.sleep(.5)
    raise RuntimeError('Serviço não ficou pronto. Consulte os logs em .local/native (não publique logs brutos).')

def configure(pg_bin,mongod):
    from lab import setup
    from seed import pg_admin,admin_settings,mongo_admin
    from pymongo import MongoClient
    import yaml
    setup()
    local=ROOT/'.local'
    native=local/'native'
    native.mkdir(exist_ok=True)
    s=admin_settings()
    pgdata=native/'pgdata'
    if not (pgdata/'PG_VERSION').exists():
        secret=native/'init-password.txt'
        secret.write_text(s['pg_admin_password'],encoding='utf-8')
        try:
            subprocess.run([str(pg_bin/'initdb.exe'),'-D',str(pgdata),'-U','postgres','--auth=scram-sha-256','--encoding=UTF8','--locale=C','--pwfile='+str(secret)],check=True,stdout=subprocess.DEVNULL)
        finally: secret.unlink(missing_ok=True)
    certs=(local/'certs').as_posix()
    (pgdata/'postgresql.auto.conf').write_text(f"""listen_addresses='127.0.0.1'
port=55432
ssl=on
ssl_cert_file='{certs}/postgres/server.crt'
ssl_key_file='{certs}/postgres/server.key'
password_encryption='scram-sha-256'
log_connections=on
log_disconnections=on
log_statement='ddl'
log_min_error_statement='panic'
log_parameter_max_length=0
log_parameter_max_length_on_error=0
logging_collector=on
log_directory='log'
log_filename='postgresql-%Y-%m-%d.log'
log_line_prefix='%m [%p] user=%u db=%d app=%a '
""",encoding='utf-8')
    hba=(ROOT/'config/pg_hba.conf').read_text(encoding='utf-8').replace('172.29.74.0/24','127.0.0.1/32')
    (pgdata/'pg_hba.conf').write_text(hba,encoding='utf-8')
    status=subprocess.run([str(pg_bin/'pg_ctl.exe'),'-D',str(pgdata),'status'],capture_output=True)
    if status.returncode:
        subprocess.run([str(pg_bin/'pg_ctl.exe'),'-D',str(pgdata),'-l',str(native/'postgres-startup.log'),'-w','start'],check=True,stdout=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    with pg_admin('postgres') as conn:
        conn.autocommit=True
        if not conn.execute("SELECT 1 FROM pg_database WHERE datname='securedb'").fetchone(): conn.execute('CREATE DATABASE securedb')
    env={**os.environ,'PGCLIENTENCODING':'UTF8','PGPASSWORD':s['pg_admin_password'],'PGSSLMODE':'verify-full','PGSSLROOTCERT':s['ca_file'],'POSTGRES_APP_PASSWORD':s['pg_app_password'],'POSTGRES_AUTH_PASSWORD':s['pg_auth_password']}
    for script in ['roles_grants','schema','rls','seeds']:
        subprocess.run([str(pg_bin/'psql.exe'),'-h','localhost','-p','55432','-U','postgres','-d','securedb','-v','ON_ERROR_STOP=1','-f',str(ROOT/'sql'/f'{script}.sql')],env=env,check=True,stdout=subprocess.DEVNULL)
    mongodata=native/'mongodata'
    mongodata.mkdir(exist_ok=True)
    mongo_conf={'storage':{'dbPath':str(mongodata)},'net':{'bindIp':'127.0.0.1','port':57017,'tls':{'mode':'requireTLS','certificateKeyFile':str(local/'certs/mongo/server.pem'),'CAFile':str(local/'certs/mongo/ca.crt'),'allowConnectionsWithoutCertificates':True}},'security':{'authorization':'enabled','javascriptEnabled':False},'systemLog':{'destination':'file','path':str(native/'mongod.log'),'logAppend':True}}
    cfg=native/'mongod.yml'
    cfg.write_text(yaml.safe_dump(mongo_conf),encoding='utf-8')
    try:
        client=mongo_admin()
        client.admin.command('ping')
    except Exception:
        process=spawn([str(mongod),'--config',str(cfg)],native/'mongo-startup.log')
        (native/'mongo.pid').write_text(str(process.pid))
        def bootstrap():
            c=MongoClient('localhost',57017,tls=True,tlsCAFile=s['ca_file'],serverSelectionTimeoutMS=1000)
            c.admin.command('ping')
            return c
        c=wait(bootstrap)
        try: c.admin.command('createUser','lab_admin',pwd=s['mongo_admin_password'],roles=[{'role':'root','db':'admin'}])
        except Exception as e:
            if getattr(e,'code',None) not in {13,51003}: raise
        finally: c.close()
        client=mongo_admin()
    role={'role':'catalog_api','privileges':[{'resource':{'db':'lab','collection':collection},'actions':['find','insert','update']} for collection in ['products','profiles']],'roles':[]}
    if not client.lab.command('rolesInfo','catalog_api')['roles']: client.lab.command('createRole',role['role'],privileges=role['privileges'],roles=[])
    if not client.lab.command('usersInfo','api_user')['users']: client.lab.command('createUser','api_user',pwd=s['mongo_app_password'],roles=[{'role':'catalog_api','db':'lab'}])
    for collection,schema in json.loads((ROOT/'nosql/schemas.json').read_text(encoding='utf-8')).items():
        opts={'validator':{'$jsonSchema':schema},'validationAction':'error','validationLevel':'strict'}
        if collection not in client.lab.list_collection_names(): client.lab.create_collection(collection,**opts)
        else: client.lab.command('collMod',collection,**opts)
    client.lab.products.create_index([('tenant_id',1),('sku',1)],unique=True)
    client.lab.profiles.create_index([('tenant_id',1),('email',1)],unique=True)
    for collection,documents in json.loads((ROOT/'nosql/seeds.json').read_text(encoding='utf-8')).items():
        for document in documents: client.lab[collection].update_one({'_id':document['_id']},{'$setOnInsert':document},upsert=True)
    client.close()
    from seed import seed_accounts
    seed_accounts()
    print('Bancos nativos prontos: TLS verificado, portas apenas em loopback. Não valida a rede Compose.')

def main():
    p=argparse.ArgumentParser()
    p.add_argument('action',choices=['start','stop'])
    p.add_argument('--pg-bin',type=Path,required=True)
    p.add_argument('--mongod',type=Path,default=Path(r'C:\Program Files\MongoDB\Server\8.0\bin\mongod.exe'))
    args=p.parse_args()
    if args.action=='start': configure(args.pg_bin,args.mongod)
    else:
        failures=[]
        pgdata=ROOT/'.local/native/pgdata'
        try:
            status=subprocess.run([str(args.pg_bin/'pg_ctl.exe'),'-D',str(pgdata),'status'],capture_output=True)
            if status.returncode==0:
                subprocess.run([str(args.pg_bin/'pg_ctl.exe'),'-D',str(pgdata),'-w','stop'],check=True)
        except Exception:failures.append('PostgreSQL')
        from seed import mongo_admin
        from pymongo.errors import AutoReconnect
        with socket.socket() as probe:
            probe.settimeout(.5)
            mongo_running=probe.connect_ex(('127.0.0.1',57017))==0
        if mongo_running:
            try:
                client=mongo_admin()
                actual=Path(client.admin.command('getCmdLineOpts')['parsed']['storage']['dbPath']).resolve()
                if actual!=(ROOT/'.local/native/mongodata').resolve():raise RuntimeError('Banco de outra instalação; parada recusada.')
                try:client.admin.command('shutdown',force=False)
                except AutoReconnect:pass
                finally:client.close()
            except Exception:failures.append('MongoDB')
        if failures:raise RuntimeError('Não foi possível confirmar a parada de: '+', '.join(failures))

if __name__=='__main__': main()
