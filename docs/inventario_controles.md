# Inventário de controles

Implementação e comprovação são independentes. Cada aprovação exige todos os testes associados. A comprovação desta execução se restringe ao perfil registrado, sem generalização para outro ambiente.

## SQL-01 - Ambiente isolado

**Risco:** Exposição e perda de dados.

**Objetivo:** Executar PostgreSQL persistente em rede restrita.

**Configuração:** `docker-compose.yml`.

**Teste positivo:** Servidor 17.x responde e tabelas persistem; contêiner ativo e rede interna observados por ENV-01.

**Teste negativo:** ENV-01 recusa banco com porta publicada, contêiner parado ou rede de dados não interna.

**Comprovação:** IMPLEMENTADO E TESTADO; cenários `test_sql_environment`, `ENV-01`.

**Evidência:** `evidencias/latest.json` e `evidencias/environment.json` (quando existente), além dos arquivos por teste em `evidencias/sql` / `evidencias/nosql` na instância que os executou.

**Risco residual:** Host Docker e volume continuam no mesmo domínio de falha.

## SQL-02 - Roles segregadas

**Risco:** Comprometimento com poder de DBA.

**Objetivo:** Segregar propriedade, leitura, escrita e autenticação.

**Configuração:** `sql/roles_grants.sql`.

**Teste positivo:** api_user herda app_read/app_write e não possui atributos administrativos.

**Teste negativo:** Membership de migration_owner ausente; SET ROLE migration_owner negado em SQL-03.

**Comprovação:** IMPLEMENTADO E TESTADO; cenários `test_sql_roles`.

**Evidência:** `evidencias/latest.json` e `evidencias/environment.json` (quando existente), além dos arquivos por teste em `evidencias/sql` / `evidencias/nosql` na instância que os executou.

**Risco residual:** Administrador e operador de migrations mantêm poder elevado.

## SQL-03 - Menor privilégio

**Risco:** DDL e leitura de credenciais pela API.

**Objetivo:** Permitir apenas operações de negócio e sessão necessárias.

**Configuração:** `sql/schema.sql`.

**Teste positivo:** SELECT autorizado e criação/atualização de pedido próprio funcionam.

**Teste negativo:** DDL, TRUNCATE, leitura de auth.accounts e escrita por perfil leitor são negados.

**Comprovação:** IMPLEMENTADO E TESTADO; cenários `test_sql_privileges`, `test_api_viewer_and_csrf`.

**Evidência:** `evidencias/latest.json` e `evidencias/environment.json` (quando existente), além dos arquivos por teste em `evidencias/sql` / `evidencias/nosql` na instância que os executou.

**Risco residual:** A conta de negócio acessa ambos os tenants sob contexto confiável.

## SQL-04 - SCRAM e origem

**Risco:** Acesso indevido ao banco.

**Objetivo:** Autenticar com SCRAM e aceitar somente origens previstas no pg_hba.

**Configuração:** `config/pg_hba.conf`.

**Teste positivo:** Senha correta funciona e verificador armazenado é SCRAM-SHA-256.

**Teste negativo:** Senha incorreta é recusada; origem 127.0.0.2 recebe SQLSTATE 28000 no perfil nativo.

**Comprovação:** IMPLEMENTADO E TESTADO; cenários `test_sql_authentication`.

**Evidência:** `evidencias/latest.json` e `evidencias/environment.json` (quando existente), além dos arquivos por teste em `evidencias/sql` / `evidencias/nosql` na instância que os executou.

**Risco residual:** SCRAM não substitui proteção do segredo e do host.

## SQL-05 - TLS verify-full

**Risco:** Interceptação do canal.

**Objetivo:** Verificar identidade do servidor e cifrar o canal PostgreSQL.

**Configuração:** `config/postgresql.conf`.

**Teste positivo:** pg_stat_ssl confirma TLS 1.2/1.3 com cliente verify-full.

**Teste negativo:** Conexão sem TLS ou com hostname divergente é recusada.

**Comprovação:** IMPLEMENTADO E TESTADO; cenários `test_sql_tls`.

**Evidência:** `evidencias/latest.json` e `evidencias/environment.json` (quando existente), além dos arquivos por teste em `evidencias/sql` / `evidencias/nosql` na instância que os executou.

**Risco residual:** CA didática local; não certifica identidade pública.

## SQL-06 - Isolamento por RLS

**Risco:** Leitura e escrita entre empresas.

**Objetivo:** Aplicar fronteira de empresa no SGBD e na API.

**Configuração:** `sql/rls.sql`.

**Teste positivo:** Empresa B opera em suas linhas; A cria e atualiza pedido próprio; SET LOCAL é limpo no commit.

**Teste negativo:** A não lê/atualiza linhas B, não insere com tenant B e não escolhe tenant no payload.

**Comprovação:** IMPLEMENTADO E TESTADO; cenários `test_sql_rls_direct`, `test_api_tenant_access`, `test_api_write_scope`, `test_sql_context_reset`.

**Evidência:** `evidencias/latest.json` e `evidencias/environment.json` (quando existente), além dos arquivos por teste em `evidencias/sql` / `evidencias/nosql` na instância que os executou.

**Risco residual:** GUC de tenant é confiada ao backend; injeção arbitrária ou API comprometida pode alterá-la.

## SQL-07 - Consultas parametrizadas

**Risco:** SQL injection.

**Objetivo:** Separar dados da sintaxe SQL e validar regras de negócio.

**Configuração:** `api/routes.py`.

**Teste positivo:** Pesquisa legítima encontra cliente da empresa; campos válidos geram pedido.

**Teste negativo:** String com aspas/OR é tratada como dado; mass assignment e tipos inválidos são rejeitados.

**Comprovação:** IMPLEMENTADO SEM VALIDAÇÃO; cenários `test_sql_injection`, `test_api_validation`.

**Evidência:** `evidencias/latest.json` e `evidencias/environment.json` (quando existente), além dos arquivos por teste em `evidencias/sql` / `evidencias/nosql` na instância que os executou.

**Risco residual:** Parametrização não decide autorização ou regras de negócio.

## SQL-08 - Trilha de auditoria

**Risco:** Ações sem rastreabilidade.

**Objetivo:** Registrar autoria, horário e operações críticas sem divulgar segredos.

**Configuração:** `api/audit.py`, `sql/schema.sql`, `config/postgresql.conf`.

**Teste positivo:** INSERT de pedido aparece no trigger; conexão, DDL e falha de login aparecem no log real.

**Teste negativo:** A API não lê auditoria de outra empresa nem exporta senha, token, corpo ou SQL do log bruto.

**Comprovação:** IMPLEMENTADO E TESTADO; cenários `test_sql_audit`.

**Evidência:** `evidencias/latest.json` e `evidencias/environment.json` (quando existente), além dos arquivos por teste em `evidencias/sql` / `evidencias/nosql` na instância que os executou.

**Risco residual:** Admin pode alterar logs; não há SIEM nem trilha imutável.

## SQL-09 - Backup e restauração

**Risco:** Perda irreversível de dados.

**Objetivo:** Demonstrar recuperação SQL a partir de cópia cifrada.

**Configuração:** `scripts/backup_restore.py`.

**Teste positivo:** pg_dump com snapshot e pg_restore em base nova produzem contagens e fingerprints iguais.

**Teste negativo:** Guardião recusa o nome da origem ou destinos fora do prefixo; divergência/tampering impede aprovação.

**Comprovação:** IMPLEMENTADO E TESTADO; cenários `test_sql_backup`.

**Evidência:** `evidencias/latest.json` e `evidencias/environment.json` (quando existente), além dos arquivos por teste em `evidencias/sql` / `evidencias/nosql` na instância que os executou.

**Risco residual:** Sem agenda, offsite, HA ou PITR; chave guardada no mesmo host.

## SQL-10 - Checklist e testes finais

**Risco:** Falsa sensação de proteção.

**Objetivo:** Consolidar os testes SQL e os limites do experimento.

**Configuração:** `tests/test_sql.py`, `tests/test_api.py`.

**Teste positivo:** Checklist final exige PASS nos cenários SQL e arquivo de riscos residuais existente.

**Teste negativo:** Falha ou ausência de cenário obrigatório impede aprovação; ENV-01 continua exigido no ambiente.

**Comprovação:** IMPLEMENTADO SEM VALIDAÇÃO; cenários `test_sql_final`.

**Evidência:** `evidencias/latest.json` e `evidencias/environment.json` (quando existente), além dos arquivos por teste em `evidencias/sql` / `evidencias/nosql` na instância que os executou.

**Risco residual:** Testes limitados aos cenários e versões registrados.

## NOSQL-01 - Ambiente isolado

**Risco:** Exposição e perda de documentos.

**Objetivo:** Executar MongoDB Community persistente e isolado.

**Configuração:** `docker-compose.yml`.

**Teste positivo:** Servidor Community 8.0 responde; contêiner e ausência de publicação são observados por ENV-01.

**Teste negativo:** Inspeção recusa publicação de porta ou rede interna ausente; não se presume Docker pelo teste nativo.

**Comprovação:** IMPLEMENTADO E TESTADO; cenários `test_mongo_environment`, `ENV-01`.

**Evidência:** `evidencias/latest.json` e `evidencias/environment.json` (quando existente), além dos arquivos por teste em `evidencias/sql` / `evidencias/nosql` na instância que os executou.

**Risco residual:** Host e volume único permanecem pontos de falha.

## NOSQL-02 - Administrador separado

**Risco:** Uso de root no runtime.

**Objetivo:** Separar a conta root da identidade da API MongoDB.

**Configuração:** `nosql/users_roles.js`.

**Teste positivo:** connectionStatus identifica api_user@lab; administrador distinto existe.

**Teste negativo:** A identidade da aplicação não aparece como lab_admin/root no runtime.

**Comprovação:** IMPLEMENTADO E TESTADO; cenários `test_mongo_admin_separation`.

**Evidência:** `evidencias/latest.json` e `evidencias/environment.json` (quando existente), além dos arquivos por teste em `evidencias/sql` / `evidencias/nosql` na instância que os executou.

**Risco residual:** Root é necessário para bootstrap e restauração didática.

## NOSQL-03 - Autenticação obrigatória

**Risco:** Acesso anônimo aos documentos.

**Objetivo:** Exigir autenticação para acessar dados MongoDB.

**Configuração:** `config/mongod.conf`.

**Teste positivo:** api_user autenticado lê produtos; login válido da aplicação funciona.

**Teste negativo:** Cliente anônimo recebe erro 13 ao ler coleção; ping anônimo não é aceito como prova de leitura.

**Comprovação:** IMPLEMENTADO E TESTADO; cenários `test_mongo_anonymous`.

**Evidência:** `evidencias/latest.json` e `evidencias/environment.json` (quando existente), além dos arquivos por teste em `evidencias/sql` / `evidencias/nosql` na instância que os executou.

**Risco residual:** Ping pode ser anônimo; operação de dados deve ser negada.

## NOSQL-04 - RBAC por coleção

**Risco:** Criação de usuários ou desvio de schema.

**Objetivo:** Restringir ações e coleções da aplicação.

**Configuração:** `nosql/users_roles.js`.

**Teste positivo:** Leitura e escrita nas coleções previstas funcionam com papel mínimo.

**Teste negativo:** usersInfo admin, createUser, collMod e escrita em coleção não concedida recebem erro 13.

**Comprovação:** IMPLEMENTADO E TESTADO; cenários `test_mongo_rbac`, `test_api_viewer_and_csrf`.

**Evidência:** `evidencias/latest.json` e `evidencias/environment.json` (quando existente), além dos arquivos por teste em `evidencias/sql` / `evidencias/nosql` na instância que os executou.

**Risco residual:** Isolamento por empresa é da API; MongoDB não implementa RLS aqui.

## NOSQL-05 - Rede restrita

**Risco:** Alcance público da porta.

**Objetivo:** Conter alcance de rede e verificar configuração efetiva.

**Configuração:** `docker-compose.yml`, `config/mongod.conf`.

**Teste positivo:** getCmdLineOpts confirma bindIp; ENV-01 inspeciona rede e PortBindings reais.

**Teste negativo:** Banco publicado ou rede não interna reprova ENV-01; 0.0.0.0 isoladamente não comprova proteção.

**Comprovação:** IMPLEMENTADO E TESTADO; cenários `test_mongo_network`, `ENV-01`.

**Evidência:** `evidencias/latest.json` e `evidencias/environment.json` (quando existente), além dos arquivos por teste em `evidencias/sql` / `evidencias/nosql` na instância que os executou.

**Risco residual:** 0.0.0.0 no contêiner depende de rede isolada e ausência de publicação.

## NOSQL-06 - TLS obrigatório

**Risco:** Canal sem verificação.

**Objetivo:** Exigir TLS e validar CA/hostname no cliente MongoDB.

**Configuração:** `config/mongod.conf`.

**Teste positivo:** Cliente com CA correta e hostname previsto consulta documentos via TLS.

**Teste negativo:** Plaintext, CA não confiável e hostname divergente são rejeitados.

**Comprovação:** IMPLEMENTADO E TESTADO; cenários `test_mongo_tls`.

**Evidência:** `evidencias/latest.json` e `evidencias/environment.json` (quando existente), além dos arquivos por teste em `evidencias/sql` / `evidencias/nosql` na instância que os executou.

**Risco residual:** TLS do banco não protege navegador HTTP local.

## NOSQL-07 - Schema no SGBD

**Risco:** Documentos inconsistentes.

**Objetivo:** Aplicar integridade documental diretamente no SGBD.

**Configuração:** `nosql/schema_validation.js`, `nosql/schemas.json`.

**Teste positivo:** Produto/perfil válido é aceito por escrita direta PyMongo, sem passar por Pydantic.

**Teste negativo:** Preço negativo e e-mail inválido são recusados pelo MongoDB com código 121.

**Comprovação:** IMPLEMENTADO E TESTADO; cenários `test_mongo_schema`.

**Evidência:** `evidencias/latest.json` e `evidencias/environment.json` (quando existente), além dos arquivos por teste em `evidencias/sql` / `evidencias/nosql` na instância que os executou.

**Risco residual:** Validação sintática não comprova veracidade dos dados.

## NOSQL-08 - Filtros tipados

**Risco:** Ampliação de consulta com operadores.

**Objetivo:** Construir buscas tipadas e literais com escopo da sessão.

**Configuração:** `api/models.py`, `api/db.py`.

**Teste positivo:** Pesquisa legítima de produto/perfil e filtro de categoria/segmento preservam a empresa.

**Teste negativo:** q[$ne], $where, objetos e parâmetros extras são recusados; .* não amplia resultados.

**Comprovação:** IMPLEMENTADO SEM VALIDAÇÃO; cenários `test_mongo_injection`, `test_profile_search`.

**Evidência:** `evidencias/latest.json` e `evidencias/environment.json` (quando existente), além dos arquivos por teste em `evidencias/sql` / `evidencias/nosql` na instância que os executou.

**Risco residual:** Filtros internos ainda precisam de revisão de autorização.

## NOSQL-09 - Backup e restauração

**Risco:** Perda de coleções.

**Objetivo:** Demonstrar restauração de documentos a partir de cópia cifrada.

**Configuração:** `scripts/backup_restore.py`.

**Teste positivo:** mongodump/mongorestore em namespace novo preservam contagens e fingerprints de ambas as coleções.

**Teste negativo:** Destino de origem é proibido; divergência de conteúdo ou mudança persistente durante dump impede PASS.

**Comprovação:** IMPLEMENTADO E TESTADO; cenários `test_mongo_backup`.

**Evidência:** `evidencias/latest.json` e `evidencias/environment.json` (quando existente), além dos arquivos por teste em `evidencias/sql` / `evidencias/nosql` na instância que os executou.

**Risco residual:** Standalone não oferece snapshot consistente multi-documento; pausar escritas.

## NOSQL-10 - Checklist e testes finais

**Risco:** Controle declarado sem prova.

**Objetivo:** Consolidar testes NoSQL e riscos residuais.

**Configuração:** `tests/test_mongo.py`.

**Teste positivo:** Checklist requer PASS em autenticação, RBAC, rede observada, TLS, schema, filtros e restore.

**Teste negativo:** Cenário obrigatório ausente/falho impede aprovação; não se declara auditoria Enterprise.

**Comprovação:** IMPLEMENTADO SEM VALIDAÇÃO; cenários `test_mongo_final`.

**Evidência:** `evidencias/latest.json` e `evidencias/environment.json` (quando existente), além dos arquivos por teste em `evidencias/sql` / `evidencias/nosql` na instância que os executou.

**Risco residual:** Community sem auditoria Enterprise; suíte não é auditoria formal.
