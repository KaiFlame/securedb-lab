"""Isolated, encrypted round trips. No drop, overwrite, or restore into source."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import secrets
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from uuid import uuid4
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from psycopg import sql
from psycopg.rows import dict_row
from seed import pg_admin, mongo_admin, admin_settings, ROOT

TABLES=['lab.tenants','lab.customers','lab.orders']

def fingerprint_rows(rows):
    canonical=sorted(json.dumps(r,sort_keys=True,default=str,ensure_ascii=False) for r in rows)
    return {'count':len(rows),'sha256':hashlib.sha256('\n'.join(canonical).encode()).hexdigest()}

def sql_fingerprints(conn):
    result={}
    with conn.cursor(row_factory=dict_row) as cur:
        for table in TABLES:
            schema,name=table.split('.')
            cur.execute(sql.SQL('SELECT * FROM {}.{}').format(sql.Identifier(schema),sql.Identifier(name)))
            result[table]=fingerprint_rows(cur.fetchall())
    return result

def mongo_fingerprints(db):
    return {name:fingerprint_rows(list(db[name].find())) for name in ['products','profiles']}

def guarded_destination(name,kind):
    prefix='restore_pg_' if kind=='sql' else 'restore_mongo_'
    if not name.startswith(prefix) or len(name)!=len(prefix)+32 or not all(c in '0123456789abcdef' for c in name[len(prefix):]):
        raise ValueError('Destino fora do namespace de restauração isolada.')
    return name

def encrypted_file(raw_path,name):
    root=Path(os.getenv('LAB_BACKUPS', '/backups' if Path('/backups').exists() else ROOT/'.local/backups'))
    root.mkdir(parents=True,exist_ok=True)
    admin_dir=Path(os.getenv('LAB_ADMIN', ROOT/'.local/admin.json')).parent
    key_path=admin_dir/'backup.key'
    if not key_path.exists(): key_path=ROOT/'.local/admin/backup.key'
    key=key_path.read_bytes()
    nonce=secrets.token_bytes(12)
    cipher=AESGCM(key)
    content=raw_path.read_bytes()
    target=root/f'{name}.aesgcm'
    blob=b'SDB1'+nonce+cipher.encrypt(nonce,content,b'SecureDB Lab v1')
    target.write_bytes(blob)
    # Restore consumes the decrypted saved artifact, proving that the saved copy works.
    saved=target.read_bytes()
    recovered=cipher.decrypt(saved[4:16],saved[16:],b'SecureDB Lab v1')
    if recovered!=content: raise RuntimeError('Verificação criptográfica falhou.')
    return target,recovered

def run_tool(args,**kwargs):
    result=subprocess.run(args,capture_output=True,**kwargs)
    if result.returncode:
        # Driver output may contain credentials or full documents. Keep it local only.
        raise RuntimeError(f'{Path(args[0]).name} falhou (código {result.returncode}); nenhum segredo foi exportado.')
    return result

def sql_roundtrip():
    s=admin_settings()
    destination=guarded_destination('restore_pg_'+uuid4().hex,'sql')
    env={**os.environ,'PGHOST':s['pg_host'],'PGPORT':str(s['pg_port']),'PGUSER':'postgres','PGPASSWORD':s['pg_admin_password'],'PGSSLMODE':'verify-full','PGSSLROOTCERT':s['ca_file']}
    with tempfile.TemporaryDirectory(prefix='securedb-backup-') as temp:
        raw=Path(temp)/'source.dump'
        start=time.perf_counter()
        with pg_admin() as source:
            source.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY')
            expected=sql_fingerprints(source)
            snapshot=source.execute('SELECT pg_export_snapshot()').fetchone()[0]
            run_tool(['pg_dump','-Fc','--snapshot='+snapshot,'-d','securedb','-f',str(raw)],env=env)
        backup_seconds=time.perf_counter()-start
        artifact,recovered=encrypted_file(raw,destination)
        raw.write_bytes(recovered)
        restore_start=time.perf_counter()
        with pg_admin('postgres') as admin:
            admin.autocommit=True
            if admin.execute('SELECT 1 FROM pg_database WHERE datname=%s',(destination,)).fetchone():
                raise RuntimeError('Destino já existe; sobrescrita proibida.')
            admin.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(destination)))
        run_tool(['pg_restore','--exit-on-error','--no-owner','--no-privileges','-d',destination,str(raw)],env=env)
        with pg_admin(destination) as restored: actual=sql_fingerprints(restored)
        if expected!=actual: raise AssertionError('Conteúdo SQL restaurado diverge da origem.')
        return {'destination':destination,'backup_seconds':round(backup_seconds,4),'restore_seconds':round(time.perf_counter()-restore_start,4),'source':expected,'restored':actual,'artifact_name':artifact.name,'encrypted':'AES-256-GCM','consistent_snapshot':True}

def mongo_roundtrip():
    from urllib.parse import quote
    s=admin_settings()
    destination=guarded_destination('restore_mongo_'+uuid4().hex,'nosql')
    uri=f"mongodb://lab_admin@{s['mongo_host']}:{s['mongo_port']}/?authSource=admin&tls=true"
    with tempfile.TemporaryDirectory(prefix='securedb-backup-') as temp:
        import yaml
        config=Path(temp)/'tool.yml'
        config.write_text(yaml.safe_dump({'password':s['mongo_admin_password']}),encoding='utf-8')
        config.chmod(0o600)
        raw=Path(temp)/'source.archive'
        common=['--uri',uri,'--config',str(config),'--sslCAFile',s['ca_file']]
        client=mongo_admin()
        expected=mongo_fingerprints(client.lab)
        start=time.perf_counter()
        run_tool(['mongodump',*common,'--db','lab','--archive='+str(raw),'--gzip'])
        backup_seconds=time.perf_counter()-start
        if expected!=mongo_fingerprints(client.lab):
            raise RuntimeError('Origem mudou durante dump standalone; repita com aplicação sem escritas.')
        artifact,recovered=encrypted_file(raw,destination)
        raw.write_bytes(recovered)
        if destination in client.list_database_names(): raise RuntimeError('Destino já existe.')
        restore_start=time.perf_counter()
        run_tool(['mongorestore',*common,'--archive='+str(raw),'--gzip','--nsInclude=lab.*','--nsFrom=lab.*','--nsTo='+destination+'.*','--stopOnError'])
        actual=mongo_fingerprints(client[destination])
        if expected!=actual: raise AssertionError('Conteúdo NoSQL restaurado diverge da origem.')
        client.close()
        return {'destination':destination,'backup_seconds':round(backup_seconds,4),'restore_seconds':round(time.perf_counter()-restore_start,4),'source':expected,'restored':actual,'artifact_name':artifact.name,'encrypted':'AES-256-GCM','consistent_snapshot':False,'limitation':'Standalone: comparação antes/depois detecta alterações persistentes; mantenha escritas pausadas.'}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--database',choices=['sql','nosql','both'],default='both')
    args=parser.parse_args()
    for kind,fn in [('sql',sql_roundtrip),('nosql',mongo_roundtrip)]:
        if args.database not in {kind,'both'}: continue
        item={'id':'BACKUP-'+kind.upper(),'timestamp':datetime.now(timezone.utc).isoformat(),'result':'PASS','observed':fn()}
        path=ROOT/'evidencias'/kind/'backup_restore.json'
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(item,ensure_ascii=False,indent=2),encoding='utf-8')
        print(f'{kind}: backup criptografado e restauração isolada verificados.')

if __name__=='__main__': main()
