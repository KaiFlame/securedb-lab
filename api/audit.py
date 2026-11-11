import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from .config import ROOT

_lock = threading.Lock()

def audit(event, actor=None, tenant=None, outcome="success"):
    path = Path(os.getenv("LAB_AUDIT", ROOT / ".local/audit/events.jsonl"))
    path.parent.mkdir(parents=True, exist_ok=True)
    # No request bodies, query strings, credentials, cookies, SQL or exception text.
    item = {"timestamp": datetime.now(timezone.utc).isoformat(), "event": event,
            "actor": str(actor) if actor else None, "tenant_id": str(tenant) if tenant else None,
            "outcome": outcome}
    with _lock, path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(item, ensure_ascii=False) + "\n")
