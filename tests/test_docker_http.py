"""HTTP real via Nginx → Uvicorn → bancos; separado do TestClient."""
import os
import re

import httpx
import pytest

pytestmark = [pytest.mark.integration, pytest.mark.skipif(
    os.getenv('LAB_DOCKER_HTTP') != '1', reason='Requer serviços Docker ativos e LAB_DOCKER_HTTP=1.')]


def test_docker_http_proxy_login_and_isolation(observed):
    from seed import admin_settings
    origin = os.getenv('LAB_ORIGIN', 'http://localhost:8080')
    headers = {'origin': origin, 'host': origin.split('://', 1)[1]}
    credentials = {a['username']: a for a in admin_settings()['accounts']}
    with httpx.Client(base_url='http://web:8080', headers=headers, timeout=15) as a, \
            httpx.Client(base_url='http://web:8080', headers=headers, timeout=15) as b:
        page = a.get('/')
        assert page.status_code == 200 and 'text/html' in page.headers['content-type']
        assert "script-src 'self'" in page.headers['content-security-policy']
        assert page.headers['x-frame-options'] == 'DENY'
        assert page.headers['x-content-type-options'] == 'nosniff'
        script = re.search(r'src="([^"]+\.js)"', page.text).group(1)
        asset = a.get(script)
        assert asset.status_code == 200 and 'javascript' in asset.headers['content-type']
        assert a.get('/api/health').json() == {'status': 'ready', 'mode': 'real-databases'}
        assert a.get('/api/orders').status_code == 401
        missing = a.get('/api/rota-inexistente')
        assert missing.status_code == 404 and 'application/json' in missing.headers['content-type']
        assert a.post('/api/auth/login', content='x' * 17000).status_code == 413
        assert a.post('/api/auth/login', json={'username': 'x', 'password': 'y'},
                      headers={'origin': 'https://untrusted.example'}).status_code == 403
        identities = []
        for client, username in [(a, 'aurora.editor'), (b, 'vertice.editor')]:
            account = credentials[username]
            login = client.post('/api/auth/login', json={'username': username, 'password': account['password']})
            assert login.status_code == 200
            cookie = login.headers['set-cookie'].lower()
            assert 'httponly' in cookie and 'samesite=strict' in cookie and 'path=/api' in cookie
            identity = login.json()
            assert identity['csrf']
            client.headers['x-csrf-token'] = identity['csrf']
            identities.append(identity)
        assert identities[0]['tenant_id'] != identities[1]['tenant_id']
        orders_b = b.get('/api/orders').json()
        assert orders_b
        order_id = orders_b[0]['id']
        assert b.get(f'/api/orders/{order_id}').status_code == 200
        assert a.get(f'/api/orders/{order_id}').status_code == 404
        for endpoint in ['products', 'profiles']:
            rows = a.get(f'/api/{endpoint}').json()
            assert rows and all(row['tenant_id'] == identities[0]['tenant_id'] for row in rows)
        rows = a.get('/api/profiles', params={'q': 'Horizonte', 'segment': 'Corporativo'}).json()
        assert rows
        assert a.post('/api/auth/logout', headers={'x-csrf-token': ''}).status_code == 403
        assert a.post('/api/auth/logout').status_code == 200
        assert a.get('/api/auth/me').status_code == 401
    observed.update(proxy='Nginx/Uvicorn real',javascript_mime='correct',health=200,
                    seeded_accounts=2,cross_tenant_order=404,oversized_body=413,
                    csrf=403,external_origin=403,logout='session invalidated')
