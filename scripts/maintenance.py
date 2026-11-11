"""Preview/remove regenerable caches only. Databases, evidence and keys excluded."""
import argparse
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[1]
ALLOWED=['.pytest_cache','api/__pycache__','scripts/__pycache__','tests/__pycache__']

def cache_targets(root=ROOT):
    root=root.resolve()
    result=[]
    for name in ALLOWED:
        path=root/name
        if path.is_symlink():raise ValueError('Cache simbólico recusado.')
        resolved=path.resolve()
        if not resolved.is_relative_to(root):raise ValueError('Caminho fora do projeto.')
        if path.is_dir():result.append(path)
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument('action',choices=['clean'])
    p.add_argument('--apply',action='store_true')
    args=p.parse_args()
    for target in cache_targets():
        print(('Remover: ' if args.apply else 'Prévia: ')+str(target.relative_to(ROOT)))
        if args.apply:shutil.rmtree(target)
    print('Bancos, backups, certificados e evidências preservados. Use --apply para efetivar a limpeza dos caches.')
if __name__=='__main__':main()
