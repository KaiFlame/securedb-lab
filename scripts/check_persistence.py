"""Compare business data across a deliberate Compose down/up; never modifies data."""
import argparse
import json
from pathlib import Path
from backup_restore import sql_fingerprints, mongo_fingerprints
from seed import pg_admin, mongo_admin


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--save', action='store_true')
    args = parser.parse_args()
    with pg_admin() as conn:
        sql = sql_fingerprints(conn)
        accounts = conn.execute('SELECT count(*) FROM auth.accounts').fetchone()[0]
    with mongo_admin() as client:
        mongo = mongo_fingerprints(client['lab'])
    snapshot = {'sql': sql, 'mongo': mongo, 'accounts': accounts}
    path = Path('/checks/persistence.json')
    if args.save:
        path.write_text(json.dumps(snapshot), encoding='utf-8')
        print('Fingerprints de persistência registrados; nenhum dado foi alterado.')
    else:
        if snapshot != json.loads(path.read_text(encoding='utf-8')):
            raise RuntimeError('Dados divergiram após reinicialização.')
        Path('/app/evidencias/persistence.json').write_text(json.dumps(
            {'check': 'compose-restart-business-data', 'result': 'PASS', 'observed': snapshot}, indent=2), encoding='utf-8')
        print('PASS: dados e contas preservados após Compose down/up.')


if __name__ == '__main__':
    main()
