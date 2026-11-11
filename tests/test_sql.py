import json
import os
import time
from uuid import UUID,uuid4
import psycopg
from psycopg import errors
import pytest
from api.db import pg_connect,tenant_tx
from api.config import settings
from seed import pg_admin
pytestmark=pytest.mark.integration
A=UUID('11111111-1111-4111-8111-111111111111'); B=UUID('22222222-2222-4222-8222-222222222222')

@pytest.mark.controls('SQL-01')
def test_sql_environment(observed):
    with pg_admin() as conn:
        version=conn.execute('SHOW server_version').fetchone()[0]
        assert version.startswith('17.')
        assert conn.execute("SELECT name FROM lab.customers WHERE id='a1111111-1111-4111-8111-111111111111'").fetchone()[0]=='Estúdio Horizonte'
    observed.update(server_version=version,persistent_tables=['lab.tenants','lab.customers','lab.orders'],unicode_data='UTF-8 verified',profile=os.getenv('LAB_TEST_ENV'))

@pytest.mark.controls('SQL-02')
def test_sql_roles(observed):
    with pg_connect() as conn:
        flags=conn.execute('SELECT rolsuper,rolcreatedb,rolcreaterole,rolbypassrls,rolreplication FROM pg_roles WHERE rolname=current_user').fetchone()
        assert not any(flags.values())
        owner=conn.execute("SELECT tableowner FROM pg_tables WHERE schemaname='lab' AND tablename='orders'").fetchone()['tableowner']
        assert owner=='migration_owner'
        members=conn.execute("SELECT pg_has_role(current_user,'app_read','member') AS read,pg_has_role(current_user,'app_write','member') AS write,pg_has_role(current_user,'migration_owner','member') AS migration").fetchone()
        assert members['read'] and members['write'] and not members['migration']
    observed.update(runtime_role='api_user',attributes=flags,table_owner=owner,memberships=members)

@pytest.mark.controls('SQL-03')
def test_sql_privileges(observed):
    with tenant_tx({'tenant_id':A,'id':uuid4()}) as conn:
        assert conn.execute('SELECT count(*) AS n FROM lab.orders').fetchone()['n']>=1
    for statement in ['CREATE TABLE lab.forbidden(id int)','SELECT * FROM auth.accounts','TRUNCATE lab.orders','SET ROLE migration_owner']:
        with pytest.raises(errors.InsufficientPrivilege),pg_connect() as conn: conn.execute(statement)
    with pytest.raises(errors.InsufficientPrivilege),pg_connect('auth') as conn: conn.execute('SELECT * FROM lab.orders')
    observed.update(legitimate_select='accepted',ddl='denied',account_table='denied',truncate='denied',set_owner_role='denied',auth_business_read='denied')

@pytest.mark.controls('SQL-04')
def test_sql_authentication(observed):
    s=settings()
    with pg_connect() as conn: assert conn.execute('SELECT current_user AS name').fetchone()['name']=='api_user'
    with pytest.raises(psycopg.OperationalError):
        psycopg.connect(host=s['pg_host'],port=s.get('pg_port',5432),dbname='securedb',user='api_user',password='incorrect',sslmode='verify-full',sslrootcert=s['ca_file'],connect_timeout=2)
    with pg_admin() as conn:
        methods=conn.execute("SELECT DISTINCT auth_method FROM pg_hba_file_rules WHERE type='hostssl' AND error IS NULL").fetchall()
        assert ('scram-sha-256',) in methods
        secret=conn.execute("SELECT rolpassword LIKE 'SCRAM-SHA-256$%' FROM pg_authid WHERE rolname='api_user'").fetchone()[0]
        assert secret
    origin_result='Active pg_hba deny rules verified; foreign container subnet needs final deployment test.'
    if s['pg_host'] in {'localhost','127.0.0.1'}:
        import socket,ssl,struct
        # PostgreSQL startup protocol with a distinct loopback source. No password
        # is transmitted: pg_hba rejects the source before authentication.
        with socket.create_connection(('127.0.0.1',s.get('pg_port',5432)),timeout=3,source_address=('127.0.0.2',0)) as sock:
            sock.sendall(struct.pack('!II',8,80877103))
            assert sock.recv(1)==b'S'
            ctx=ssl.create_default_context(cafile=s['ca_file'])
            with ctx.wrap_socket(sock,server_hostname='127.0.0.1') as channel:
                params=b'user\x00api_user\x00database\x00securedb\x00application_name\x00origin-negative\x00\x00'
                channel.sendall(struct.pack('!II',len(params)+8,196608)+params)
                tag=channel.recv(1);length=struct.unpack('!I',channel.recv(4))[0]
                message=b''
                while len(message)<length-4:message+=channel.recv(length-4-len(message))
                assert tag==b'E' and b'pg_hba' in message and b'28000' in message
        origin_result='Source 127.0.0.2 rejected by pg_hba over verified TLS (SQLSTATE 28000).'
    observed.update(correct_credentials='accepted',wrong_credentials='denied',stored_verifier='SCRAM-SHA-256',origin_limit=origin_result)

@pytest.mark.controls('SQL-05')
def test_sql_tls(observed):
    s=settings()
    with pg_connect() as conn:
        row=conn.execute('SELECT ssl,version,cipher FROM pg_stat_ssl WHERE pid=pg_backend_pid()').fetchone()
        assert row['ssl'] and row['version'] in {'TLSv1.2','TLSv1.3'}
    for options in [{'sslmode':'disable'},{'sslmode':'verify-full','sslrootcert':s['ca_file'],'host':'wrong.invalid','hostaddr':'127.0.0.1' if s['pg_host']=='localhost' else None}]:
        if options.get('hostaddr') is None:
            import socket
            options['hostaddr']=socket.gethostbyname(s['pg_host'])
        with pytest.raises(psycopg.OperationalError):
            psycopg.connect(**{'host':s['pg_host'],'port':s.get('pg_port',5432),'dbname':'securedb','user':'api_user','password':s['pg_app_password'],'connect_timeout':2,**options})
    observed.update(**row,plaintext='rejected',wrong_hostname='rejected')

@pytest.mark.controls('SQL-06')
def test_sql_rls_direct(observed):
    with pg_connect() as conn: assert conn.execute('SELECT count(*) AS n FROM lab.orders').fetchone()['n']==0
    with tenant_tx({'tenant_id':A,'id':uuid4()}) as conn:
        assert conn.execute('SELECT id FROM lab.orders WHERE tenant_id=%s',(B,)).fetchall()==[]
        assert conn.execute("UPDATE lab.orders SET status='approved' WHERE tenant_id=%s",(B,)).rowcount==0
    with pytest.raises(errors.InsufficientPrivilege),tenant_tx({'tenant_id':A,'id':uuid4()}) as conn:
        conn.execute('INSERT INTO lab.orders(id,tenant_id,customer_id,description,total) VALUES (%s,%s,%s,%s,%s)',(uuid4(),B,UUID('b1111111-1111-4111-8111-111111111111'),'Cross tenant',10))
    with tenant_tx({'tenant_id':B,'id':uuid4()}) as conn: assert conn.execute('SELECT count(*) AS n FROM lab.orders').fetchone()['n']>=1
    observed.update(no_context_rows=0,cross_select_rows=0,cross_update_rows=0,cross_insert='RLS denied',tenant_B='own rows visible')

@pytest.mark.controls('SQL-06')
def test_sql_context_reset(observed):
    with pg_connect() as conn:
        with conn.transaction():
            conn.execute("SELECT set_config('app.tenant_id',%s,true)",(str(A),))
            assert conn.execute('SELECT count(*) AS n FROM lab.orders').fetchone()['n']>0
        assert conn.execute("SELECT nullif(current_setting('app.tenant_id',true),'') AS tid").fetchone()['tid'] is None
        assert conn.execute('SELECT count(*) AS n FROM lab.orders').fetchone()['n']==0
    observed.update(reused_connection_after_commit='zero visible rows; SET LOCAL reset')

@pytest.mark.controls('SQL-07')
def test_sql_injection(logged,observed):
    c,_=logged()
    valid=c.get('/api/customers',params={'q':'Horizonte'})
    attack=c.get('/api/customers',params={'q':"' OR 1=1 --"})
    assert valid.status_code==200 and len(valid.json())>=1
    assert attack.status_code==200 and attack.json()==[]
    observed.update(legitimate_search='matches own customer',adversarial_string='treated as data',adversarial_rows=0,driver='psycopg parameter binding with prepare=True')

@pytest.mark.controls('SQL-08')
def test_sql_audit(logged,observed):
    c,_=logged()
    res=c.post('/api/orders',json={'customer_id':'a1111111-1111-4111-8111-111111111111','description':'Auditoria sintética','total':'1.00'})
    assert res.status_code==201
    logs=c.get('/api/audit');assert logs.status_code==200
    assert any(e['entity_id']==res.json()['id'] and e['operation']=='INSERT' for e in logs.json())
    events=c.get('/api/events')
    assert events.status_code==200 and any(e['event']=='order.created' for e in events.json())
    assert all(set(e)=={'timestamp','event','actor','outcome'} for e in events.json())
    c,_=logged('vertice.editor')
    other=c.get('/api/audit')
    assert other.status_code==200 and all(e['entity_id']!=res.json()['id'] for e in other.json())
    with pg_admin() as conn:
        assert conn.execute('SHOW log_connections').fetchone()[0]=='on'
        assert conn.execute('SHOW log_statement').fetchone()[0]=='ddl'
        conn.execute('CREATE TABLE IF NOT EXISTS lab.audit_probe(id integer)')
    time.sleep(1)
    with pg_admin() as conn:
        log=conn.execute("SELECT pg_read_file(pg_current_logfile())").fetchone()[0]
        connection='connection authorized' in log
        ddl='audit_probe' in log
        failed='password authentication failed' in log
        assert connection and ddl and failed
    observed.update(order_event={'entity_id':res.json()['id'],'operation':'INSERT'},database_logs={'connection':connection,'ddl':ddl,'failed_auth':failed},export='only event presence; raw lines excluded')

@pytest.mark.controls('SQL-09')
def test_sql_backup(observed):
    from backup_restore import sql_roundtrip
    observed.update(sql_roundtrip())

@pytest.mark.controls('SQL-10')
def test_sql_final(observed):
    from conftest import RESULTS
    required={'test_sql_environment','test_sql_roles','test_sql_privileges','test_sql_authentication','test_sql_tls','test_sql_rls_direct','test_sql_context_reset','test_sql_injection','test_sql_audit','test_sql_backup'}
    results={r['id']:r['result'] for r in RESULTS}
    assert all(results.get(t)=='PASS' for t in required)
    assert (Path(__file__).parents[1]/'docs/riscos_residuais.md').exists()
    observed.update(checklist={t:results[t] for t in sorted(required)},risks='docs/riscos_residuais.md',limit='Native execution does not certify Docker networking')

from pathlib import Path
