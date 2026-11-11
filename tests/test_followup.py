import json
from pathlib import Path
from uuid import uuid4
import pytest

@pytest.mark.integration
@pytest.mark.controls('NOSQL-08')
def test_profile_search(logged,observed):
    """Pesquisa literal de nome/e-mail/segmento e rejeição de operador/tenant."""
    client,a=logged()
    rows=client.get('/api/profiles',params={'q':'Horizonte','segment':'Corporativo'})
    assert rows.status_code==200 and rows.json()
    assert all(r['tenant_id']==a['tenant_id'] and r['segment']=='Corporativo' for r in rows.json())
    assert client.get('/api/profiles',params={'q':'nucleo@example.test'}).json()==[]
    assert client.get('/api/profiles',params={'q':'.*'}).json()==[]
    assert client.get('/api/profiles',params={'q[$ne]':''}).status_code==422
    assert client.get('/api/profiles',params={'q':'$where'}).status_code==422
    assert client.get('/api/profiles',params={'segment':'inexistente'}).status_code==422
    assert client.get('/api/profiles',params={'tenant_id':str(uuid4())}).status_code==422
    observed.update(valid_search=200,cross_tenant_results=0,regex='literal',operator_query=422,invalid_segment=422,tenant_override=422)

def test_environment_export_and_profile_scope(monkeypatch,tmp_path,observed):
    import api.evidence as module
    monkeypatch.setattr(module,'evidence_root',lambda:tmp_path)
    env={'id':'ENV-01','result':'PASS','timestamp':'2026-11-11T12:00:00Z','controls':['SQL-01','NOSQL-01','NOSQL-05']}
    (tmp_path/'environment.json').write_text(json.dumps(env),encoding='utf-8')
    report={'environment':'Docker Compose / bancos reais / TLS verificado','tests':[]}
    path=tmp_path/'latest.json';path.write_text(json.dumps(report),encoding='utf-8')
    _,exported=module.control_results()
    assert exported['tests']==[env]
    report['environment']='Windows nativo / bancos reais'
    path.write_text(json.dumps(report),encoding='utf-8')
    _,exported=module.control_results()
    assert exported['tests']==[]
    observed.update(environment_receipt='included in Docker export; excluded from native result')

def test_control_details_have_real_source_and_specific_scenarios(observed):
    root=Path(__file__).resolve().parents[1]
    controls=json.loads((root/'docs/controls.json').read_text(encoding='utf-8'))
    assert len(controls)==20
    assert len({c['positive'] for c in controls})==20
    assert len({c['negative'] for c in controls})==20
    for c in controls:
        cfg=c['configuration']
        assert c['objective'] and cfg['excerpt']
        actual=(root/cfg['path']).read_text(encoding='utf-8')
        assert cfg['excerpt'] in actual
        assert '.env'!=cfg['path'] and not cfg['path'].startswith('.local/')
    observed.update(controls=20,source_excerpts='match versioned files',scenarios='specific; positive and negative')

def test_desktop_paths_and_cleanup_stay_inside_project(tmp_path,observed):
    import desktop,maintenance
    assert all(p.is_relative_to(desktop.ROOT) for p in desktop.tool_paths().values())
    with pytest.raises(ValueError):desktop.project_path('../outside')
    (tmp_path/'api/__pycache__').mkdir(parents=True)
    (tmp_path/'.local/native').mkdir(parents=True)
    targets=maintenance.cache_targets(tmp_path)
    assert targets==[tmp_path/'api/__pycache__']
    observed.update(paths='project-relative',traversal='denied',database_cleanup='not selected')

def test_desktop_restart_clears_old_stop_before_gui(monkeypatch,tmp_path,observed):
    import desktop,sys
    marker=tmp_path/'stop.request';marker.write_text('old run',encoding='ascii')
    monkeypatch.setattr(desktop,'STATE_DIR',tmp_path)
    monkeypatch.setattr(desktop,'STOP_FILE',marker)
    monkeypatch.setattr(desktop,'IS_WINDOWS',True)
    monkeypatch.setattr(desktop,'write_state',lambda *a,**k:None)
    class Lock:
        def close(self):pass
    monkeypatch.setattr(desktop,'lock_instance',lambda:Lock())
    monkeypatch.setattr(desktop,'DesktopRuntime',lambda:object())
    checked=[]
    def verify_gui(*args):
        assert not marker.exists()
        checked.append(True)
    monkeypatch.setattr(desktop,'gui',verify_gui)
    monkeypatch.setattr(sys,'argv',['desktop.py','start','--no-browser'])
    desktop.main()
    assert checked==[True]
    observed.update(previous_stop_marker='cleared before GUI polling')
