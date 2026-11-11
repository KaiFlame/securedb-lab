import hashlib
import secrets
import threading
import time
from collections import OrderedDict
from datetime import datetime, timedelta, timezone
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, InvalidHashError
from fastapi import Depends, HTTPException, Request
from .db import pg_connect

hasher = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=2)
dummy_hash = hasher.hash(secrets.token_urlsafe(32))

def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()

class LoginLimiter:
    def __init__(self):
        self.entries = OrderedDict()
        self.lock = threading.Lock()

    def check(self, ip):
        with self.lock:
            now = time.monotonic()
            while self.entries and next(iter(self.entries.values()))[0] < now - 300:
                self.entries.popitem(last=False)
            start, count = self.entries.get(ip, (now, 0))
            if now - start > 300:
                start, count = now, 0
            if count >= 15:
                raise HTTPException(429, "Muitas tentativas. Aguarde cinco minutos.")
            self.entries[ip] = (start, count + 1)
            self.entries.move_to_end(ip)
            while len(self.entries) > 10000:
                self.entries.popitem(last=False)

limiter = LoginLimiter()

def authenticate(username, password):
    with pg_connect("auth") as conn:
        user = conn.execute("SELECT id, username, password_hash, tenant_id, role, display_name, tenant_name FROM auth.accounts WHERE username=%s AND active", (username,)).fetchone()
    try:
        valid = hasher.verify(user["password_hash"] if user else dummy_hash, password)
    except (VerificationError, InvalidHashError):
        valid = False
    if not user or not valid:
        return None
    user.pop("password_hash")
    return user

def new_session(user):
    token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
    expires = datetime.now(timezone.utc) + timedelta(hours=2)
    with pg_connect("auth") as conn:
        conn.execute("DELETE FROM auth.sessions WHERE expires_at < now()")
        conn.execute("INSERT INTO auth.sessions(token_hash, account_id, csrf, expires_at) VALUES (%s,%s,%s,%s)", (digest(token), user["id"], csrf, expires))
    return token, csrf

def current_user(request: Request):
    token = request.cookies.get("sdb_session")
    if not token or len(token) > 100:
        raise HTTPException(401, "Entre para acessar o laboratório.")
    with pg_connect("auth") as conn:
        user = conn.execute("""SELECT a.id,a.username,a.tenant_id,a.role,a.display_name,a.tenant_name,s.csrf
            FROM auth.sessions s JOIN auth.accounts a ON a.id=s.account_id
            WHERE token_hash=%s AND expires_at>now() AND a.active""", (digest(token),)).fetchone()
    if not user:
        raise HTTPException(401, "Sessão expirada. Entre novamente.")
    request.state.user = user
    if request.method not in {"GET", "HEAD", "OPTIONS"}:
        supplied = request.headers.get("x-csrf-token", "")
        if not secrets.compare_digest(supplied, user["csrf"]):
            raise HTTPException(403, "Atualize a sessão antes de enviar alterações.")
    return user

def editor(user=Depends(current_user)):
    if user["role"] not in {"editor", "admin"}:
        raise HTTPException(403, "Seu perfil permite somente leitura.")
    return user
