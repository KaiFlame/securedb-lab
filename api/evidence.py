import json
import os
from collections import deque
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from .config import ROOT, evidence_root
from .security import current_user
from .db import tenant_tx

router=APIRouter(prefix='/api')

def control_results():
    inventory=json.loads((ROOT/'docs/controls.json').read_text(encoding='utf-8'))
    report_path=evidence_root()/'latest.json'
    report=json.loads(report_path.read_text(encoding='utf-8')) if report_path.exists() else {'tests':[],'timestamp':None}
    tests={t['id']:t for t in report['tests']}
    env_path=evidence_root()/'environment.json'
    if env_path.exists() and report.get('environment','').startswith('Docker Compose'):
        env=json.loads(env_path.read_text(encoding='utf-8'))
        tests[env['id']]=env
    for c in inventory:
        relevant=[tests[k] for k in c['required_tests'] if k in tests]
        complete=len(relevant)==len(c['required_tests'])
        c['status']='fail' if any(t['result']=='FAIL' for t in relevant) else 'pass' if complete and all(t['result']=='PASS' for t in relevant) else 'pending'
        c['tests']=relevant
        c['last_run']=max((t['timestamp'] for t in relevant),default=None)
        c['evidence']=f"evidencias/{'sql' if c['lab']=='SQL' else 'nosql'}/" if relevant else None
    return inventory,{**report,'tests':list(tests.values())}

@router.get('/controls')
def controls(user=Depends(current_user)):
    controls,report=control_results()
    return {'controls':controls,'timestamp':report.get('timestamp'),'tests':report.get('tests',[]),'environment':report.get('environment','não executado')}

@router.get('/audit')
def events(user=Depends(current_user)):
    with tenant_tx(user) as conn:
        return conn.execute('SELECT id,at,actor,operation,entity_id FROM audit.events ORDER BY id DESC LIMIT 50').fetchall()

@router.get('/events')
def recent_events(user=Depends(current_user)):
    path=Path(os.getenv('LAB_AUDIT',ROOT/'.local/audit/events.jsonl'))
    if not path.exists():return []
    with path.open('rb') as stream:
        size=path.stat().st_size
        start=max(size-65536,0)
        stream.seek(start)
        if start:stream.readline()
        lines=deque(stream,maxlen=500)
    result=[]
    for line in reversed(lines):
        try:item=json.loads(line)
        except (ValueError,UnicodeDecodeError):continue
        if item.get('tenant_id')==str(user['tenant_id']):
            result.append({k:item.get(k) for k in ['timestamp','event','actor','outcome']})
        if len(result)>=30:break
    return result

DOCS={'arquitetura','inventario_controles','questoes_dissertativas','simuladores','riscos_residuais','relatorio_final','rastreabilidade','roteiro_apresentacao','requisitos_fontes','github','uso_desktop'}

@router.get('/documents/{name}')
def document(name: str,user=Depends(current_user)):
    if name not in DOCS:
        raise HTTPException(404,'Documento não encontrado.')
    path=ROOT/'docs'/f'{name}.md'
    if not path.exists():
        raise HTTPException(404,'Documento ainda não gerado.')
    return {'name':name,'content':path.read_text(encoding='utf-8')}

@router.get('/evidence/export')
def export(user=Depends(current_user)):
    from fastapi.responses import JSONResponse
    _,report=control_results()
    return JSONResponse(report,headers={'Content-Disposition':'attachment; filename="securedb-resultados.json"'})
