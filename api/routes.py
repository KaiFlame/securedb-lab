from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from psycopg import errors
from pymongo.errors import DuplicateKeyError, WriteError
from .models import Login, OrderCreate, OrderStatus, Product, Profile, CatalogQuery, ProfileQuery
from .security import authenticate, new_session, current_user, editor, limiter, digest
from .db import pg_connect, tenant_tx, mongo_client, catalog_filter, profile_filter
from .audit import audit
from .config import settings

router = APIRouter(prefix="/api")

@router.post("/auth/login")
def login(body: Login, request: Request, response: Response):
    limiter.check(request.client.host)
    user = authenticate(body.username, body.password)
    if not user:
        audit("login", outcome="denied")
        raise HTTPException(401, "Usuário ou senha inválidos.")
    token, csrf = new_session(user)
    response.set_cookie("sdb_session", token, httponly=True, secure=settings().get("secure_cookie", False), samesite="strict", max_age=7200, path="/api")
    audit("login", user["id"], user["tenant_id"])
    return {**user, "csrf": csrf}

@router.get("/auth/me")
def me(user=Depends(current_user)):
    return user

@router.post("/auth/logout")
def logout(request: Request, response: Response, user=Depends(current_user)):
    with pg_connect("auth") as conn:
        conn.execute("DELETE FROM auth.sessions WHERE token_hash=%s", (digest(request.cookies["sdb_session"]),))
    response.delete_cookie("sdb_session", path="/api")
    audit("logout", user["id"], user["tenant_id"])
    return {"ok": True}

@router.get("/customers")
def customers(q: str = Query("", max_length=80), user=Depends(current_user)):
    with tenant_tx(user) as conn:
        return conn.execute("SELECT id,name,email FROM lab.customers WHERE name ILIKE %s ORDER BY name LIMIT 100", (f"%{q}%",), prepare=True).fetchall()

@router.get("/orders")
def orders(user=Depends(current_user)):
    with tenant_tx(user) as conn:
        return conn.execute("""SELECT o.id,o.customer_id,c.name AS customer,o.description,o.total,o.status,o.created_at
            FROM lab.orders o JOIN lab.customers c ON (c.tenant_id,c.id)=(o.tenant_id,o.customer_id)
            ORDER BY o.created_at DESC LIMIT 100""").fetchall()

@router.get("/orders/{order_id}")
def order(order_id: UUID, user=Depends(current_user)):
    with tenant_tx(user) as conn:
        row = conn.execute("SELECT id,customer_id,description,total,status,created_at FROM lab.orders WHERE id=%s", (order_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Pedido não encontrado.")
    return row

@router.post("/orders", status_code=201)
def create_order(body: OrderCreate, user=Depends(editor)):
    try:
        with tenant_tx(user) as conn:
            if not conn.execute("SELECT 1 FROM lab.customers WHERE id=%s", (body.customer_id,)).fetchone():
                raise HTTPException(404, "Cliente não encontrado.")
            row = conn.execute("""INSERT INTO lab.orders(id,tenant_id,customer_id,description,total)
                VALUES (%s,%s,%s,%s,%s) RETURNING id,description,total,status""",
                (uuid4(), user["tenant_id"], body.customer_id, body.description, body.total)).fetchone()
    except errors.IntegrityError:
        raise HTTPException(422, "Os dados do pedido são inconsistentes.") from None
    audit("order.created", user["id"], user["tenant_id"])
    return row

@router.patch("/orders/{order_id}/status")
def update_order(order_id: UUID, body: OrderStatus, user=Depends(editor)):
    with tenant_tx(user) as conn:
        row = conn.execute("SELECT status FROM lab.orders WHERE id=%s FOR UPDATE", (order_id,)).fetchone()
        if not row:
            raise HTTPException(404, "Pedido não encontrado.")
        transitions = {"draft": {"approved", "cancelled"}, "approved": {"shipped", "cancelled"}, "shipped": set(), "cancelled": set()}
        if body.status not in transitions[row["status"]]:
            raise HTTPException(409, "Transição de status não permitida.")
        conn.execute("UPDATE lab.orders SET status=%s WHERE id=%s", (body.status, order_id))
    audit("order.status_changed", user["id"], user["tenant_id"])
    return {"id": str(order_id), "status": body.status}

@router.get("/products")
def products(query: CatalogQuery = Query(), user=Depends(current_user)):
    return list(mongo_client().lab.products.find(catalog_filter(user["tenant_id"], query.q, query.category)).sort("name", 1).limit(query.limit))

@router.get("/profiles")
def profiles(query: ProfileQuery = Query(), user=Depends(current_user)):
    return list(mongo_client().lab.profiles.find(profile_filter(user["tenant_id"],query.q,query.segment)).sort("name", 1).limit(query.limit))

def save_document(collection, body, user, document_id=None):
    coll = mongo_client().lab[collection]
    data = body.model_dump()
    data["tenant_id"] = str(user["tenant_id"])
    try:
        if document_id:
            result = coll.update_one({"_id": str(document_id), "tenant_id": data["tenant_id"]}, {"$set": data})
            if not result.matched_count:
                raise HTTPException(404, "Documento não encontrado.")
            data["_id"] = str(document_id)
        else:
            data["_id"] = str(uuid4())
            coll.insert_one(data)
    except DuplicateKeyError:
        raise HTTPException(409, "Já existe um item com esse código.") from None
    except WriteError:
        raise HTTPException(422, "O MongoDB recusou o documento por validação de esquema.") from None
    audit(f"{collection}.saved", user["id"], user["tenant_id"])
    return data

@router.post("/products", status_code=201)
def create_product(body: Product, user=Depends(editor)):
    return save_document("products", body, user)

@router.put("/products/{document_id}")
def edit_product(document_id: UUID, body: Product, user=Depends(editor)):
    return save_document("products", body, user, document_id)

@router.post("/profiles", status_code=201)
def create_profile(body: Profile, user=Depends(editor)):
    return save_document("profiles", body, user)

@router.put("/profiles/{document_id}")
def edit_profile(document_id: UUID, body: Profile, user=Depends(editor)):
    return save_document("profiles", body, user, document_id)
