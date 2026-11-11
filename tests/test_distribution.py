"""Portable setup and rejection of unsafe Docker inspection records."""
import copy
import json
import os
import stat
from pathlib import Path

import pytest


def test_setup_preserves_credentials_certificates_and_port(monkeypatch, tmp_path, observed):
    import lab
    monkeypatch.setattr(lab, 'ROOT', tmp_path)
    monkeypatch.delenv('WEB_PORT', raising=False)
    lab.setup()
    secrets = (tmp_path / '.local/secrets.json').read_bytes()
    cert = (tmp_path / '.local/certs/postgres/server.crt').read_bytes()
    key = (tmp_path / '.local/admin/backup.key').read_bytes()
    env = tmp_path / '.env'
    env.write_text(env.read_text().replace('WEB_PORT=8080', 'WEB_PORT=18081'))
    lab.setup()
    assert (tmp_path / '.local/secrets.json').read_bytes() == secrets
    assert (tmp_path / '.local/certs/postgres/server.crt').read_bytes() == cert
    assert (tmp_path / '.local/admin/backup.key').read_bytes() == key
    assert lab.configured_port() == 18081
    runtime = json.loads((tmp_path / '.local/runtime/runtime.json').read_text())
    assert 'http://localhost:18081' in runtime['allowed_origins']
    assert len(json.loads(secrets)['accounts']) == 3
    if os.name != 'nt':
        assert stat.S_IMODE(env.stat().st_mode) == 0o600
        assert stat.S_IMODE((tmp_path / '.local').stat().st_mode) == 0o700
        assert stat.S_IMODE((tmp_path / '.local/runtime/runtime.json').stat().st_mode) == 0o644
        assert stat.S_IMODE((tmp_path / '.local/certs/client').stat().st_mode) == 0o755
    observed.update(setup='idempotent',port='preserved from .env',credentials='local and stable')


@pytest.mark.parametrize('port', ['0', '1023', '65536', 'invalid'])
def test_setup_rejects_invalid_port(monkeypatch, tmp_path, port):
    import lab
    monkeypatch.setattr(lab, 'ROOT', tmp_path)
    monkeypatch.setenv('WEB_PORT', port)
    with pytest.raises(ValueError):
        lab.configured_port()


def test_environment_inspection_rejects_unsafe_topology():
    from bootstrap import validate_environment
    network = {'Name': 'securedb-lab_data', 'Internal': True}
    containers = [{'service': name, 'running': True, 'image': name,
                   'port_bindings': {}, 'networks': {network['Name']: {}}}
                  for name in ['postgres', 'mongo']]
    assert validate_environment(containers, network)['result'] == 'PASS'
    cases = []
    for key, value in [('running', False), ('port_bindings', {'5432/tcp': [{}]}),
                       ('networks', {'securedb-lab_data': {}, 'public': {}})]:
        altered = copy.deepcopy(containers)
        altered[0][key] = value
        cases.append((altered, network))
    cases.extend([(containers[:1], network), (containers, {**network, 'Internal': False})])
    for records, net in cases:
        with pytest.raises(ValueError):
            validate_environment(records, net)


def test_build_contexts_exclude_host_dependencies_and_private_data():
    root = Path(__file__).resolve().parents[1]
    ignored = (root / '.dockerignore').read_text().splitlines()
    web = (root / 'web/.dockerignore').read_text().splitlines()
    assert {'.local', '.env', '.venv', '**/node_modules', '.git'} <= set(ignored)
    assert {'node_modules', 'dist', '.env*'} <= set(web)
    for name in ['iniciar.command', 'parar.command', 'testar.command', 'scripts/docker.sh']:
        assert b'\r' not in (root / name).read_bytes()
