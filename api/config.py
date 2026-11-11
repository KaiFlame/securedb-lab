import json
import os
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

@lru_cache
def settings():
    path = Path(os.getenv("LAB_RUNTIME", ROOT / ".local/runtime.json"))
    if not path.is_file():
        raise RuntimeError("Execute python scripts/lab.py setup antes de iniciar a API.")
    return json.loads(path.read_text(encoding="utf-8"))

def evidence_root():
    return Path(os.getenv("LAB_EVIDENCE", ROOT / "evidencias"))
