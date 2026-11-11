SET ROLE migration_owner;
CREATE TABLE IF NOT EXISTS lab.tenants (
 id uuid PRIMARY KEY, name text NOT NULL CHECK(length(name) BETWEEN 3 AND 100)
);
CREATE TABLE IF NOT EXISTS lab.customers (
 id uuid NOT NULL, tenant_id uuid NOT NULL REFERENCES lab.tenants(id),
 name text NOT NULL CHECK(length(name) BETWEEN 3 AND 100), email text NOT NULL,
 PRIMARY KEY(tenant_id,id), UNIQUE(tenant_id,email)
);
CREATE TABLE IF NOT EXISTS lab.orders (
 id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES lab.tenants(id), customer_id uuid NOT NULL,
 description text NOT NULL CHECK(length(description) BETWEEN 3 AND 200),
 total numeric(10,2) NOT NULL CHECK(total>0 AND total<=1000000),
 status text NOT NULL DEFAULT 'draft' CHECK(status IN ('draft','approved','shipped','cancelled')),
 created_at timestamptz NOT NULL DEFAULT now(),
 FOREIGN KEY(tenant_id,customer_id) REFERENCES lab.customers(tenant_id,id)
);
CREATE INDEX IF NOT EXISTS orders_tenant_idx ON lab.orders(tenant_id,created_at);
CREATE TABLE IF NOT EXISTS auth.accounts (
 id uuid PRIMARY KEY, username text UNIQUE NOT NULL, password_hash text NOT NULL,
 tenant_id uuid NOT NULL REFERENCES lab.tenants(id), tenant_name text NOT NULL,
 role text NOT NULL CHECK(role IN ('editor','viewer','admin')), display_name text NOT NULL,
 active boolean NOT NULL DEFAULT true
);
CREATE TABLE IF NOT EXISTS auth.sessions (
 token_hash text PRIMARY KEY, account_id uuid NOT NULL REFERENCES auth.accounts(id),
 csrf text NOT NULL, expires_at timestamptz NOT NULL
);
CREATE INDEX IF NOT EXISTS sessions_expiry_idx ON auth.sessions(expires_at);
CREATE TABLE IF NOT EXISTS audit.events (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, at timestamptz NOT NULL DEFAULT now(),
 actor text NOT NULL, tenant_id uuid NOT NULL, operation text NOT NULL, entity_id uuid NOT NULL
);
CREATE OR REPLACE FUNCTION audit.order_event() RETURNS trigger
 LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog AS $$
 BEGIN
   INSERT INTO audit.events(actor,tenant_id,operation,entity_id)
   VALUES (coalesce(nullif(current_setting('app.actor_id',true),''),'database-session'),NEW.tenant_id,TG_OP,NEW.id);
   RETURN NEW;
 END $$;
DROP TRIGGER IF EXISTS orders_audit ON lab.orders;
CREATE TRIGGER orders_audit AFTER INSERT OR UPDATE ON lab.orders FOR EACH ROW EXECUTE FUNCTION audit.order_event();
GRANT SELECT ON lab.tenants,lab.customers,lab.orders TO app_read;
GRANT INSERT ON lab.orders TO app_write;
GRANT UPDATE(status) ON lab.orders TO app_write;
GRANT SELECT ON audit.events TO app_read;
GRANT SELECT ON auth.accounts TO auth_user;
GRANT SELECT,INSERT,DELETE ON auth.sessions TO auth_user;
RESET ROLE;
