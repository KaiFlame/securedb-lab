"""Host-independent setup and validation of narrowly scoped Docker observations."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from lab import ROOT, setup, write_json


def validate_environment(containers, network):
    if network.get('Internal') is not True:
        raise ValueError('A rede de dados precisa ser interna.')
    network_name = network['Name']
    observed = []
    if {c['service'] for c in containers} != {'postgres', 'mongo'}:
        raise ValueError('Inspeção incompleta dos dois bancos.')
    for c in containers:
        if c.get('running') is not True or c.get('port_bindings'):
            raise ValueError('Banco parado ou com porta publicada.')
        if set(c.get('networks', {})) != {network_name}:
            raise ValueError('Banco conectado fora da rede de dados.')
        observed.append({'service': c['service'], 'image': c['image'],
                         'running': True, 'published_ports': []})
    return {'id': 'ENV-01', 'controls': ['SQL-01', 'NOSQL-01', 'NOSQL-05'],
            'result': 'PASS', 'timestamp': datetime.now(timezone.utc).isoformat(),
            'objective': 'Contêineres ativos, rede interna exclusiva e bancos sem portas publicadas',
            'observed': observed, 'internal_network': True}


def main():
    action = sys.argv[1] if len(sys.argv) > 1 else 'setup'
    if action == 'setup':
        setup()
    elif action == 'diagnose':
        folder = ROOT / '.local/inspection'
        containers = [json.loads((folder / f'{name}.json').read_text())
                      for name in ['postgres', 'mongo']]
        network = json.loads((folder / 'network.json').read_text())
        write_json(ROOT / 'evidencias/environment.json', validate_environment(containers, network))
        print('ENV-01 PASS: observação efetiva de contêineres, portas e rede interna.')
    else:
        raise SystemExit('Ação inválida para o bootstrap.')


if __name__ == '__main__':
    main()
