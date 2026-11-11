# Matriz de rastreabilidade

Perfil observado: Windows nativo / bancos reais / TLS verificado / Compose não executado.

A falta de ENV-01 impede comprovar os itens de implantação em contêineres. Os demais PASS documentam a execução real no perfil informado.

| ID | Requisito | Status | Arquivo / evidência |
|---|---|---|---|
| SQL-01 | Ambiente isolado | IMPLEMENTADO SEM VALIDAÇÃO | `docker-compose.yml`; `test_sql_environment`, `ENV-01` |
| SQL-02 | Roles segregadas | IMPLEMENTADO E TESTADO | `sql/roles_grants.sql`; `test_sql_roles` |
| SQL-03 | Menor privilégio | IMPLEMENTADO E TESTADO | `sql/schema.sql`; `test_sql_privileges` |
| SQL-04 | SCRAM e origem | IMPLEMENTADO E TESTADO | `config/pg_hba.conf`; `test_sql_authentication` |
| SQL-05 | TLS verify-full | IMPLEMENTADO E TESTADO | `config/postgresql.conf`; `test_sql_tls` |
| SQL-06 | Isolamento por RLS | IMPLEMENTADO E TESTADO | `sql/rls.sql`; `test_sql_rls_direct`, `test_api_tenant_access`, `test_api_write_scope`, `test_sql_context_reset` |
| SQL-07 | Consultas parametrizadas | IMPLEMENTADO E TESTADO | `api/routes.py`; `test_sql_injection`, `test_api_validation` |
| SQL-08 | Trilha de auditoria | IMPLEMENTADO E TESTADO | `api/audit.py`; `test_sql_audit` |
| SQL-09 | Backup e restauração | IMPLEMENTADO E TESTADO | `scripts/backup_restore.py`; `test_sql_backup` |
| SQL-10 | Checklist e testes finais | IMPLEMENTADO E TESTADO | `tests/test_sql.py`; `test_sql_final` |
| NOSQL-01 | Ambiente isolado | IMPLEMENTADO SEM VALIDAÇÃO | `docker-compose.yml`; `test_mongo_environment`, `ENV-01` |
| NOSQL-02 | Administrador separado | IMPLEMENTADO E TESTADO | `nosql/users_roles.js`; `test_mongo_admin_separation` |
| NOSQL-03 | Autenticação obrigatória | IMPLEMENTADO E TESTADO | `config/mongod.conf`; `test_mongo_anonymous` |
| NOSQL-04 | RBAC por coleção | IMPLEMENTADO E TESTADO | `nosql/users_roles.js`; `test_mongo_rbac` |
| NOSQL-05 | Rede restrita | IMPLEMENTADO SEM VALIDAÇÃO | `docker-compose.yml`; `test_mongo_network`, `ENV-01` |
| NOSQL-06 | TLS obrigatório | IMPLEMENTADO E TESTADO | `config/mongod.conf`; `test_mongo_tls` |
| NOSQL-07 | Schema no SGBD | IMPLEMENTADO E TESTADO | `nosql/schema_validation.js`; `test_mongo_schema` |
| NOSQL-08 | Filtros tipados | IMPLEMENTADO E TESTADO | `api/models.py`; `test_mongo_injection` |
| NOSQL-09 | Backup e restauração | IMPLEMENTADO E TESTADO | `scripts/backup_restore.py`; `test_mongo_backup` |
| NOSQL-10 | Checklist e testes finais | IMPLEMENTADO E TESTADO | `tests/test_mongo.py`; `test_mongo_final` |
| Q-01 | Enunciado original e resposta em cinco partes | IMPLEMENTADO SEM VALIDAÇÃO | `docs/questoes_dissertativas.md`, questão 1; revisão individual do aluno pendente |
| Q-02 | Enunciado original e resposta em cinco partes | IMPLEMENTADO SEM VALIDAÇÃO | `docs/questoes_dissertativas.md`, questão 2; revisão individual do aluno pendente |
| Q-03 | Enunciado original e resposta em cinco partes | IMPLEMENTADO SEM VALIDAÇÃO | `docs/questoes_dissertativas.md`, questão 3; revisão individual do aluno pendente |
| Q-04 | Enunciado original e resposta em cinco partes | IMPLEMENTADO SEM VALIDAÇÃO | `docs/questoes_dissertativas.md`, questão 4; revisão individual do aluno pendente |
| Q-05 | Enunciado original e resposta em cinco partes | IMPLEMENTADO SEM VALIDAÇÃO | `docs/questoes_dissertativas.md`, questão 5; revisão individual do aluno pendente |
| Q-06 | Enunciado original e resposta em cinco partes | IMPLEMENTADO SEM VALIDAÇÃO | `docs/questoes_dissertativas.md`, questão 6; revisão individual do aluno pendente |
| Q-07 | Enunciado original e resposta em cinco partes | IMPLEMENTADO SEM VALIDAÇÃO | `docs/questoes_dissertativas.md`, questão 7; revisão individual do aluno pendente |
| Q-08 | Enunciado original e resposta em cinco partes | IMPLEMENTADO SEM VALIDAÇÃO | `docs/questoes_dissertativas.md`, questão 8; revisão individual do aluno pendente |
| Q-09 | Enunciado original e resposta em cinco partes | IMPLEMENTADO SEM VALIDAÇÃO | `docs/questoes_dissertativas.md`, questão 9; revisão individual do aluno pendente |
| Q-10 | Enunciado original e resposta em cinco partes | IMPLEMENTADO SEM VALIDAÇÃO | `docs/questoes_dissertativas.md`, questão 10; revisão individual do aluno pendente |
| ENT-01 | Git local e README | IMPLEMENTADO E TESTADO | README.md; git status; preflight |
| ENT-02 | Scripts e configurações | IMPLEMENTADO E TESTADO | scripts/; sql/; nosql/; execução nativa |
| ENT-03 | React/FastAPI e CRUD | IMPLEMENTADO E TESTADO | web/; api/; testes integrados e frontend |
| ENT-04 | Diagrama e fronteiras | IMPLEMENTADO SEM VALIDAÇÃO | docs/arquitetura.md; revisão do aluno |
| ENT-05 | Evidências sanitizadas | IMPLEMENTADO E TESTADO | evidencias/entrega/; manifesto SHA-256 |
| ENT-06 | Relatório Markdown/PDF | IMPLEMENTADO E TESTADO | docs/relatorio_final.md; docs/relatorio_final.pdf; validação visual registrada |
| ENT-07 | Simuladores antes/depois | PENDENTE | docs/simuladores.md; evidencias/simuladores/COLETA_PENDENTE.md |
| ENT-08 | Execução Compose/CI remota | IMPLEMENTADO SEM VALIDAÇÃO | docker-compose.yml; .github/workflows; ENV-01 pendente |
| ENT-09 | Preparação GitHub | IMPLEMENTADO E TESTADO | docs/github.md; .gitignore; preflight; sem remote |
| ENT-10 | Identificação e RA | PENDENTE | Preencher campos acadêmicos no relatório |
