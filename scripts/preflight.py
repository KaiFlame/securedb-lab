"""Review only publishable checkout files; never display matched secret values."""
import json
from pathlib import Path
import re
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]

def main():
    result=subprocess.run(['git','ls-files','-z','--cached','--others','--exclude-standard'],cwd=ROOT,capture_output=True,check=True)
    paths=sorted(set(p for p in result.stdout.decode().split('\0') if p))
    secrets=[]
    local=ROOT/'.local/secrets.json'
    if local.exists():
        data=json.loads(local.read_text(encoding='utf-8'))
        secrets.extend(v for k,v in data.items() if isinstance(v,str) and 'password' in k)
        secrets.extend(a['password'] for a in data.get('accounts',[]))
    bad=[]
    for name in paths:
        path=ROOT/name
        if not path.is_file():continue
        if name=='.env' or name.startswith('.local/') or path.suffix in {'.key','.pem','.p12','.dump','.aesgcm'}:
            bad.append({'file':name,'reason':'sensitive path'})
            continue
        if path.stat().st_size>8_000_000:bad.append({'file':name,'reason':'large file requires manual review'})
        content=path.read_bytes()
        if any(s.encode() in content for s in secrets):bad.append({'file':name,'reason':'generated credential detected'})
        if re.search(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',content):bad.append({'file':name,'reason':'private key detected'})
    item={'check':'publishable-checkout-secret-scan','result':'FAIL' if bad else 'PASS','candidate_files':len(paths),'findings':bad,'scope':'Tracked and nonignored untracked files only; no complete history/dependency assurance.'}
    print(json.dumps(item,ensure_ascii=False,indent=2))
    sys.exit(bool(bad))

if __name__=='__main__':main()
