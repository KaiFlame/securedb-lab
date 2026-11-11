"""Package only Git-eligible source, after secret preflight; no .git or .local."""
import argparse
from pathlib import Path
import subprocess
import sys
import zipfile
ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=ROOT/'release/SecureDB_Lab.zip')
    args=parser.parse_args()
    subprocess.run([sys.executable,str(ROOT/'scripts/preflight.py')],cwd=ROOT,check=True)
    data=subprocess.check_output(['git','ls-files','-z','--cached','--others','--exclude-standard'],cwd=ROOT)
    paths=sorted(set(p for p in data.decode().split('\0') if p))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(args.output,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for name in paths:
            path=ROOT/name
            if path.is_file() and path.resolve()!=args.output.resolve():
                info=zipfile.ZipInfo.from_file(path,'securedb-lab/'+name)
                info.create_system=3
                mode=0o100755 if path.suffix in {'.sh','.command'} else 0o100644
                info.external_attr=mode<<16
                info.compress_type=zipfile.ZIP_DEFLATED
                archive.writestr(info,path.read_bytes())
    with zipfile.ZipFile(args.output) as archive:
        assert not any('/.local/' in n or n.endswith('/.env') or '/node_modules/' in n or '/.git/' in n for n in archive.namelist())
    print(f'Pacote público preparado: {args.output.resolve()}')

if __name__=='__main__':main()
