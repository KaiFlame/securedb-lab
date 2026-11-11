"""Real browser-origin HTTP smoke for the running Windows desktop installation."""
import os,re
import httpx
import pytest
pytestmark=[pytest.mark.integration,pytest.mark.skipif(os.getenv('LAB_DESKTOP_HTTP')!='1',reason='Smoke desktop opcional: requer inicializador local e LAB_DESKTOP_HTTP=1.')]

def test_desktop_http_proxy_and_assets(observed):
    from seed import admin_settings
    import desktop
    account=next(a for a in admin_settings()['accounts'] if a['username']=='aurora.editor')
    with httpx.Client(base_url='http://127.0.0.1:5173',timeout=10,headers={'origin':'http://127.0.0.1:5173'}) as client:
        identity=client.get('/desktop-health')
        assert identity.status_code==200 and identity.json()['root_id']==desktop.ROOT_ID
        assert client.get('/api/health').json()['status']=='ready'
        assert client.get('/api/orders').status_code==401
        page=client.get('/');assert page.status_code==200
        script=re.search(r'src="([^"]+\.js)"',page.text).group(1)
        asset=client.get(script)
        assert asset.status_code==200 and 'javascript' in asset.headers['content-type']
        assert "script-src 'self'" in page.headers['content-security-policy']
        assert client.get('/assets/').status_code==403
        assert client.get('/.local/secrets.json').status_code==404
        assert client.post('/api/auth/login',json={'username':account['username'],'password':account['password']},headers={'origin':'https://untrusted.example'}).status_code==403
        login=client.post('/api/auth/login',json={'username':account['username'],'password':account['password']})
        assert login.status_code==200 and 'HttpOnly' in login.headers['set-cookie']
        client.headers['x-csrf-token']=login.json()['csrf']
        result=client.get('/api/profiles',params={'q':'Horizonte','segment':'Corporativo'})
        assert result.status_code==200 and result.json()
        assert all(p['tenant_id']==login.json()['tenant_id'] for p in result.json())
        report=client.get('/api/evidence/export');assert report.status_code==200 and isinstance(report.json()['tests'],list)
        controls=client.get('/api/controls').json()['controls']
        assert len(controls)==20 and all(c['objective'] and c['configuration']['excerpt'] for c in controls)
        assert client.post('/api/auth/logout').status_code==200
        assert client.get('/api/orders').status_code==401
    observed.update(actual_origin='http://127.0.0.1:5173',health=200,javascript_asset='correct MIME',authentication='real login/logout through proxy',untrusted_origin=403,private_file=404,directory_listing=403,profile_search=200,evidence_export=200,control_details=20)
