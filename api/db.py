from contextlib import contextmanager
from functools import lru_cache
import re
import psycopg
from psycopg.rows import dict_row
from pymongo import MongoClient
from .config import settings

def pg_connect(identity="app"):
    s = settings()
    return psycopg.connect(host=s["pg_host"], port=s.get("pg_port", 5432),
        dbname="securedb", user="api_user" if identity == "app" else "auth_user",
        password=s["pg_app_password" if identity == "app" else "pg_auth_password"],
        sslmode="verify-full", sslrootcert=s["ca_file"], connect_timeout=5,
        row_factory=dict_row, application_name="securedb-api")

@contextmanager
def tenant_tx(user):
    # A new connection per request avoids cross-request context leakage. SET LOCAL
    # also confines both settings to this transaction if a pool is added later.
    with pg_connect() as conn:
        conn.execute("SELECT set_config('app.tenant_id', %s, true)", (str(user["tenant_id"]),))
        conn.execute("SELECT set_config('app.actor_id', %s, true)", (str(user["id"]),))
        yield conn

@lru_cache
def mongo_client():
    s = settings()
    return MongoClient(s["mongo_host"], s.get("mongo_port", 27017),
        username="api_user", password=s["mongo_app_password"], authSource="lab",
        tls=True, tlsCAFile=s["ca_file"], serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000, appname="securedb-api")

def catalog_filter(tenant_id, q="", category=None):
    result = {"tenant_id": str(tenant_id)}
    if q:
        result["name"] = {"$regex": re.escape(q), "$options": "i"}
    if category:
        result["category"] = category
    return result

def profile_filter(tenant_id, q="", segment=None):
    result={"tenant_id":str(tenant_id)}
    if q:
        literal={"$regex":re.escape(q),"$options":"i"}
        result["$or"]=[{"name":literal},{"email":literal}]
    if segment:result["segment"]=segment
    return result
