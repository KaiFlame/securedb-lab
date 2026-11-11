SET ROLE migration_owner;
ALTER TABLE lab.tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE lab.tenants FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_boundary ON lab.tenants;
CREATE POLICY tenant_boundary ON lab.tenants TO app_read,app_write
 USING (id = nullif(current_setting('app.tenant_id',true),'')::uuid)
 WITH CHECK (id = nullif(current_setting('app.tenant_id',true),'')::uuid);
ALTER TABLE lab.customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE lab.customers FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_boundary ON lab.customers;
CREATE POLICY tenant_boundary ON lab.customers TO app_read,app_write
 USING (tenant_id = nullif(current_setting('app.tenant_id',true),'')::uuid)
 WITH CHECK (tenant_id = nullif(current_setting('app.tenant_id',true),'')::uuid);
ALTER TABLE lab.orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE lab.orders FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_boundary ON lab.orders;
CREATE POLICY tenant_boundary ON lab.orders TO app_read,app_write
 USING (tenant_id = nullif(current_setting('app.tenant_id',true),'')::uuid)
 WITH CHECK (tenant_id = nullif(current_setting('app.tenant_id',true),'')::uuid);
ALTER TABLE audit.events ENABLE ROW LEVEL SECURITY;
-- The SECURITY DEFINER trigger owner must append events. API cannot append/delete them.
DROP POLICY IF EXISTS tenant_audit ON audit.events;
CREATE POLICY tenant_audit ON audit.events FOR SELECT TO app_read
 USING (tenant_id = nullif(current_setting('app.tenant_id',true),'')::uuid);
RESET ROLE;
