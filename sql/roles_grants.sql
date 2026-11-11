-- Run only through the bootstrap administrator; secrets come from the environment.
SET log_statement = 'none';
\getenv app_password POSTGRES_APP_PASSWORD
\getenv auth_password POSTGRES_AUTH_PASSWORD
SELECT 'CREATE ROLE migration_owner NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS'
 WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname='migration_owner') \gexec
SELECT 'CREATE ROLE app_read NOLOGIN' WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname='app_read') \gexec
SELECT 'CREATE ROLE app_write NOLOGIN' WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname='app_write') \gexec
SELECT format('CREATE ROLE api_user LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD %L', :'app_password')
 WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname='api_user') \gexec
SELECT format('CREATE ROLE auth_user LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD %L', :'auth_password')
 WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname='auth_user') \gexec
GRANT app_read, app_write TO api_user;
REVOKE ALL ON DATABASE securedb FROM PUBLIC;
GRANT CONNECT ON DATABASE securedb TO api_user,auth_user;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
CREATE SCHEMA IF NOT EXISTS lab AUTHORIZATION migration_owner;
CREATE SCHEMA IF NOT EXISTS auth AUTHORIZATION migration_owner;
CREATE SCHEMA IF NOT EXISTS audit AUTHORIZATION migration_owner;
GRANT USAGE ON SCHEMA lab TO app_read,app_write;
GRANT USAGE ON SCHEMA auth TO auth_user;
GRANT USAGE ON SCHEMA audit TO app_read;
ALTER DEFAULT PRIVILEGES FOR ROLE migration_owner REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;
RESET log_statement;
