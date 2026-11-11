import json
import os
from pathlib import Path
import sys
from datetime import datetime,timezone
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
RESULTS=[]

def pytest_collection_modifyitems(config,items):
    if os.getenv('LAB_INTEGRATION')!='1':
        for item in items:
            if 'integration' in item.keywords: item.add_marker(pytest.mark.skip(reason='Bancos reais não solicitados; use LAB_INTEGRATION=1.'))

@pytest.fixture
def observed(request):
    result={}
    request.node._observed=result
    return result

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item,call):
    outcome=yield
    report=outcome.get_result()
    if report.when=='call' or report.when=='setup' and report.skipped or report.when=='setup' and report.failed:
        controls=[]
        for mark in item.iter_markers('controls'): controls.extend(mark.args)
        result={'id':item.name,'controls':list(controls),'objective':(item.obj.__doc__ or item.name).strip(),
            'result':'PASS' if report.passed else 'SKIP' if report.skipped else 'FAIL',
            'timestamp':datetime.now(timezone.utc).isoformat(),'observed':getattr(item,'_observed',{}),
            'duration_seconds':round(report.duration,4)}
        if not report.passed: result['note']='Cenário não executado: bancos indisponíveis/não solicitados.' if report.skipped else 'Verificar saída local do pytest. Stack trace não exportado para evitar segredos.'
        lab='sql' if any(c.startswith('SQL-') for c in controls) else 'nosql' if any(c.startswith('NOSQL-') for c in controls) else 'app'
        path=ROOT/'evidencias'/lab/f'{item.name}.json'
        path.parent.mkdir(parents=True,exist_ok=True)
        result['artifact']=path.relative_to(ROOT).as_posix()
        path.write_text(json.dumps(result,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
        RESULTS.append(result)

def pytest_sessionfinish(session,exitstatus):
    report={'timestamp':datetime.now(timezone.utc).isoformat(),'environment':os.getenv('LAB_TEST_ENV','unitário local; integração não executada'),
        'exit_code':int(exitstatus),'tests':RESULTS}
    name='latest.json' if os.getenv('LAB_INTEGRATION')=='1' else 'unit.json'
    (ROOT/'evidencias'/name).write_text(json.dumps(report,ensure_ascii=False,indent=2,default=str),encoding='utf-8')

@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    from api.main import app
    from api.security import limiter
    limiter.entries.clear()
    with TestClient(app,raise_server_exceptions=True) as c:
        c.headers['origin']=os.getenv('LAB_ORIGIN','http://localhost:8080')
        yield c

@pytest.fixture
def logged(client):
    from seed import admin_settings
    def identity(username='aurora.editor'):
        account=next(a for a in admin_settings()['accounts'] if a['username']==username)
        result=client.post('/api/auth/login',json={'username':username,'password':account['password']})
        assert result.status_code==200
        client.headers['x-csrf-token']=result.json()['csrf']
        return client,result.json()
    return identity
