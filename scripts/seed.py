import json
import os
import sys
from pathlib import Path
from uuid import UUID
import psycopg
from argon2 import PasswordHasher
from pymongo import MongoClient

ROOT=Path(__file__).resolve().parents[1]

def admin_settings():
    return json.loads(Path(os.getenv('LAB_ADMIN',ROOT/'.local/admin.json')).read_text(encoding='utf-8'))

def pg_admin(dbname='securedb'):
    s=admin_settings()
    return psycopg.connect(host=s['pg_host'],port=s['pg_port'],dbname=dbname,user='postgres',password=s['pg_admin_password'],sslmode='verify-full',sslrootcert=s['ca_file'],connect_timeout=5)

def mongo_admin():
    s=admin_settings()
    return MongoClient(s['mongo_host'],s['mongo_port'],username='lab_admin',password=s['mongo_admin_password'],authSource='admin',tls=True,tlsCAFile=s['ca_file'],serverSelectionTimeoutMS=5000)

def seed_accounts():
    s=admin_settings()
    hasher=PasswordHasher(time_cost=3,memory_cost=65536,parallelism=2)
    tenants={'A':('11111111-1111-4111-8111-111111111111','Aurora Comércio'),'B':('22222222-2222-4222-8222-222222222222','Vértice Tecnologia')}
    with pg_admin() as conn:
        conn.execute((ROOT/'sql/seeds.sql').read_text(encoding='utf-8'))
        for i,account in enumerate(s['accounts'],1):
            tid,tname=tenants[account['tenant']]
            conn.execute('''INSERT INTO auth.accounts(id,username,password_hash,tenant_id,tenant_name,role,display_name)
             VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT(username) DO NOTHING''',
             (UUID(int=100+i),account['username'],hasher.hash(account['password']),UUID(tid),tname,account['role'],account['username']))
    print('Dados SQL e contas sintéticas preservados/semeados. Nenhuma senha foi impressa.')

if __name__=='__main__': seed_accounts()
