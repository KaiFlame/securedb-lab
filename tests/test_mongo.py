import json
from pathlib import Path
import socket
import ssl
from uuid import uuid4
from pymongo import MongoClient
from pymongo.errors import OperationFailure,WriteError,ServerSelectionTimeoutError,ConnectionFailure
import pytest
from api.config import settings
from api.db import mongo_client
from seed import mongo_admin
pytestmark=pytest.mark.integration

@pytest.mark.controls('NOSQL-01')
def test_mongo_environment(observed):
    version=mongo_admin().server_info()['version']
    assert version.startswith('8.0.')
    observed.update(server_version=version,edition='Community')

@pytest.mark.controls('NOSQL-02')
def test_mongo_admin_separation(observed):
    status=mongo_client().admin.command('connectionStatus')
    users=status['authInfo']['authenticatedUsers']
    assert users==[{'user':'api_user','db':'lab'}]
    admin_users=mongo_admin().admin.command('usersInfo','lab_admin')['users']
    assert admin_users and admin_users[0]['user']=='lab_admin'
    observed.update(runtime_identity=users,admin_separate=True)

@pytest.mark.controls('NOSQL-03')
def test_mongo_anonymous(observed):
    s=settings();anon=MongoClient(s['mongo_host'],s.get('mongo_port',27017),tls=True,tlsCAFile=s['ca_file'],serverSelectionTimeoutMS=2000)
    with pytest.raises(OperationFailure) as exc: anon.lab.products.find_one()
    assert exc.value.code==13
    anon.close()
    observed.update(anonymous_data_read='denied',mongodb_code=13,note='Unauthenticated ping is not a data access test.')

@pytest.mark.controls('NOSQL-04')
def test_mongo_rbac(observed):
    client=mongo_client()
    assert client.lab.products.find_one()
    for fn in [lambda:client.admin.command('usersInfo',1),lambda:client.lab.command('createUser','forbidden',pwd='not-a-real-password',roles=[]),lambda:client.lab.command('collMod','products',validationAction='warn'),lambda:client.lab['ungranted'].insert_one({'name':'test'})]:
        with pytest.raises(OperationFailure) as exc:fn()
        assert exc.value.code==13
    observed.update(collection_read='accepted',admin_users='denied',create_user='denied',modify_validator='denied',other_collection='denied')

@pytest.mark.controls('NOSQL-05')
def test_mongo_network(observed):
    opts=mongo_admin().admin.command('getCmdLineOpts')['parsed']
    bind=opts['net']['bindIp']
    assert bind in {'127.0.0.1','0.0.0.0'}
    observed.update(bindIp=bind,note='Loopback in native profile; Compose requires separate ENV-01 runtime inspection.')

@pytest.mark.controls('NOSQL-06')
def test_mongo_tls(observed):
    s=settings();host=s['mongo_host'];port=s.get('mongo_port',27017)
    assert mongo_client().lab.products.find_one()
    for options in [{'tls':False},{'tls':True}]:
        bad=MongoClient(host,port,username='api_user',password=s['mongo_app_password'],authSource='lab',serverSelectionTimeoutMS=1500,connectTimeoutMS=1000,**options)
        try:
            with pytest.raises((ConnectionFailure,ServerSelectionTimeoutError)):bad.lab.products.find_one()
        finally:bad.close()
    context=ssl.create_default_context(cafile=s['ca_file'])
    with socket.create_connection((host,port),timeout=3) as sock:
        with pytest.raises(ssl.SSLCertVerificationError):context.wrap_socket(sock,server_hostname='wrong.invalid')
    with socket.create_connection((host,port),timeout=3) as sock:
        with context.wrap_socket(sock,server_hostname=host) as tls: version=tls.version()
    observed.update(verified_connection=version,plaintext='rejected',untrusted_ca='rejected',wrong_hostname='rejected')

@pytest.mark.controls('NOSQL-07')
def test_mongo_schema(observed):
    good={'_id':str(uuid4()),'tenant_id':'11111111-1111-4111-8111-111111111111','name':'Schema test','sku':'T-'+uuid4().hex[:12].upper(),'category':'Software','price_cents':100,'active':True}
    result=mongo_client().lab.products.insert_one(good)
    assert result.acknowledged
    invalid={**good,'_id':str(uuid4()),'sku':'I-'+uuid4().hex[:12].upper(),'price_cents':-10}
    with pytest.raises(WriteError) as exc:mongo_client().lab.products.insert_one(invalid)
    assert exc.value.code==121
    profile={'_id':str(uuid4()),'tenant_id':good['tenant_id'],'name':'Perfil schema','email':'schema.'+uuid4().hex+'@example.test','segment':'Essencial','active':True}
    assert mongo_client().lab.profiles.insert_one(profile).acknowledged
    with pytest.raises(WriteError) as bad:mongo_client().lab.profiles.insert_one({**profile,'_id':str(uuid4()),'email':'invalido'})
    assert bad.value.code==121
    observed.update(valid_product='accepted by MongoDB',invalid_product={'code':121},valid_profile='accepted by MongoDB',invalid_profile={'code':121},validation_layer='direct PyMongo write; Pydantic bypassed for this test')

@pytest.mark.controls('NOSQL-08')
def test_mongo_injection(logged,observed):
    c,_=logged()
    assert c.get('/api/products',params={'q[$ne]':''}).status_code==422
    assert c.get('/api/products',params={'q':'$where'}).status_code==422
    assert c.get('/api/products',params={'q':'.*'}).json()==[]
    assert c.get('/api/products',params={'q':'Estação'}).status_code==200
    observed.update(operator_object=422,where=422,regex_metacharacters='literal, zero results')

@pytest.mark.controls('NOSQL-09')
def test_mongo_backup(observed):
    from backup_restore import mongo_roundtrip
    observed.update(mongo_roundtrip())

@pytest.mark.controls('NOSQL-10')
def test_mongo_final(observed):
    from conftest import RESULTS
    required={'test_mongo_environment','test_mongo_admin_separation','test_mongo_anonymous','test_mongo_rbac','test_mongo_network','test_mongo_tls','test_mongo_schema','test_mongo_injection','test_mongo_backup'}
    results={r['id']:r['result'] for r in RESULTS}
    assert all(results.get(t)=='PASS' for t in required)
    observed.update(checklist={t:results[t] for t in sorted(required)},audit_limit='Community server logs and API logs; no Enterprise audit')
