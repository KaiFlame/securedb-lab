import time
import uuid
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from psycopg import OperationalError
from pymongo.errors import PyMongoError
from .routes import router
from .evidence import router as evidence_router
from .config import settings
from .audit import audit

app = FastAPI(title="SecureDB Lab", version="1.0.0", docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "api", "testserver"])

@app.middleware("http")
async def safeguards(request: Request, call_next):
    request_id = uuid.uuid4().hex
    if request.method not in {"GET", "HEAD", "OPTIONS"}:
        origin = request.headers.get("origin")
        allowed = settings().get("allowed_origins", ["http://localhost:8080", "http://127.0.0.1:8080"])
        if origin not in allowed:
            return JSONResponse({"detail": "Origem não autorizada."}, 403)
    size = request.headers.get("content-length", "0")
    if not size.isdecimal() or int(size) > 16384:
        return JSONResponse({"detail": "Solicitação excede o limite permitido."}, 413)
    try:
        response = await call_next(request)
    except (OperationalError, PyMongoError):
        audit("database.unavailable", outcome="error")
        response = JSONResponse({"detail": "Banco indisponível. Verifique o ambiente local.", "request_id": request_id}, 503)
    response.headers.update({"X-Content-Type-Options": "nosniff", "X-Frame-Options": "DENY",
        "Referrer-Policy": "no-referrer", "Cache-Control": "no-store", "X-Request-ID": request_id})
    return response

@app.exception_handler(Exception)
async def unexpected(request, exc):
    audit("application.error", outcome="error")
    return JSONResponse({"detail": "Não foi possível concluir a operação."}, 500)

@app.get("/api/health")
def health():
    from .db import pg_connect, mongo_client
    with pg_connect("auth") as conn:
        conn.execute("SELECT 1").fetchone()
    mongo_client().admin.command("ping")
    return {"status": "ready", "mode": "real-databases"}

app.include_router(router)
app.include_router(evidence_router)
