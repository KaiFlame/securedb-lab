from uuid import uuid4
import pytest
pytestmark=pytest.mark.integration
B_ORDER='e1111111-1111-4111-8111-111111111111'
A_CUSTOMER='a1111111-1111-4111-8111-111111111111'
B_CUSTOMER='b1111111-1111-4111-8111-111111111111'

@pytest.mark.controls('SQL-04','NOSQL-03')
def test_api_authentication(client,logged,observed):
    """Login aceito/negado, sessão invalidada e endpoint sem identidade."""
    assert client.get('/api/orders').status_code==401
    bad=client.post('/api/auth/login',json={'username':'aurora.editor','password':'incorreta'})
    assert bad.status_code==401
    c,user=logged()
    cookie=c.cookies.get('sdb_session')
    assert cookie and user['tenant_name']=='Aurora Comércio'
    assert c.cookies.get('sdb_session') is not None
    assert c.post('/api/auth/logout').status_code==200
    assert c.get('/api/orders').status_code==401
    observed.update(unauthenticated=401,bad_password=401,valid_login=200,logout='invalidates session')

@pytest.mark.controls('SQL-06')
def test_api_tenant_access(logged,observed):
    """Empresa A não lê ID da B; B consulta o mesmo ID normalmente."""
    c,a=logged()
    assert c.get('/api/orders/'+B_ORDER).status_code==404
    assert all(o['id']!=B_ORDER for o in c.get('/api/orders').json())
    c,b=logged('vertice.editor')
    assert c.get('/api/orders/'+B_ORDER).status_code==200
    observed.update(A_reads_B=404,B_reads_B=200,tenant_source='authenticated account')

@pytest.mark.controls('SQL-06')
def test_api_write_scope(logged,observed):
    """SELECT/INSERT/UPDATE entre empresas e operação legítima na A."""
    c,a=logged()
    payload={'customer_id':B_CUSTOMER,'description':'Teste de escopo','total':'10.00'}
    assert c.post('/api/orders',json=payload).status_code==404
    assert c.patch('/api/orders/'+B_ORDER+'/status',json={'status':'approved'}).status_code==404
    payload['customer_id']=A_CUSTOMER
    created=c.post('/api/orders',json=payload)
    assert created.status_code==201
    oid=created.json()['id']
    assert c.patch('/api/orders/'+oid+'/status',json={'status':'approved'}).status_code==200
    assert c.patch('/api/orders/'+oid+'/status',json={'status':'approved'}).status_code==409
    observed.update(cross_tenant_insert=404,cross_tenant_update=404,own_insert=201,own_update=200,invalid_transition=409)

@pytest.mark.controls('SQL-03','NOSQL-04')
def test_api_viewer_and_csrf(logged,observed):
    c,user=logged('aurora.leitor')
    assert c.get('/api/orders').status_code==200
    assert c.post('/api/orders',json={'customer_id':A_CUSTOMER,'description':'Acesso negado','total':'2.00'}).status_code==403
    c,user=logged()
    c.headers['x-csrf-token']='invalid'
    assert c.post('/api/auth/logout').status_code==403
    observed.update(viewer_read=200,viewer_write=403,invalid_csrf=403)

@pytest.mark.controls('SQL-07','NOSQL-08')
def test_api_validation(logged,observed):
    c,user=logged()
    assert c.post('/api/orders',json={'customer_id':A_CUSTOMER,'description':'Pedido','total':'5.00','tenant_id':str(uuid4())}).status_code==422
    assert c.get('/api/products',params={'q[$ne]':''}).status_code==422
    assert c.get('/api/products',params={'q':'{"$ne":null}'}).status_code==422
    assert c.get('/api/products',params={'limit':'10000'}).status_code==422
    assert c.post('/api/products',json={'name':'Produto','sku':'TEST','category':'Software','price_cents':{'$gt':0}}).status_code==422
    observed.update(extra_tenant=422,operator_query=422,operator_string=422,object_price=422,oversized_limit=422)

@pytest.mark.controls('NOSQL-08')
def test_api_mongo_tenant_and_crud(logged,observed):
    c,a=logged()
    assert all(d['tenant_id']==str(a['tenant_id']) for d in c.get('/api/products').json())
    body={'name':'Produto de teste','sku':'T-'+uuid4().hex[:12].upper(),'category':'Software','price_cents':1000,'active':True}
    res=c.post('/api/products',json=body);assert res.status_code==201
    pid=res.json()['_id'];body['name']='Produto atualizado'
    assert c.put('/api/products/'+pid,json=body).status_code==200
    profile={'name':'Perfil de teste','email':uuid4().hex+'@example.test','segment':'Essencial','active':True}
    res=c.post('/api/profiles',json=profile);assert res.status_code==201
    profile['segment']='Corporativo'
    assert c.put('/api/profiles/'+res.json()['_id'],json=profile).status_code==200
    c,b=logged('vertice.editor')
    assert c.put('/api/products/'+pid,json=body).status_code==404
    assert all(d['tenant_id']==str(b['tenant_id']) for d in c.get('/api/profiles').json())
    observed.update(product_create=201,product_update=200,profile_create=201,profile_update=200,cross_tenant_update=404)
