# Dez questões dissertativas

Enunciados originais preservados. As respostas abaixo são subsídios técnicos para revisão individual do aluno, e não declaração de autoria do grupo. As configurações foram implementadas; a validação observada e seu perfil devem ser conferidos em `evidencias/entrega/resultado_integrado.json` e no relatório.

## 1. Explique por que a aplicação não deve utilizar uma conta administrativa do PostgreSQL. Relacione sua resposta às roles criadas no laboratório e aos princípios de least privilege e segregação de funções.

**Conceito.** Mínimo privilégio limita cada identidade às operações necessárias; segregação de funções separa uso, evolução e administração do banco.

**Risco.** Uma credencial de DBA na API transforma uma falha de aplicação em capacidade de criar usuários, alterar políticas, ler todos os dados ou remover estruturas.

**Configuração implementada.** `migration_owner` é NOLOGIN e proprietário das estruturas. `app_read` e `app_write` são grupos sem login, herdados por `api_user`. Este não tem SUPERUSER, CREATEDB, CREATEROLE, REPLICATION ou BYPASSRLS. `auth_user` acessa contas/sessões e não tabelas de negócio. O bootstrap usa administrador separado.

**Evidência observável.** `test_sql_roles` verifica atributos, proprietário e memberships; `test_sql_privileges` aceita SELECT legítimo e nega CREATE TABLE, TRUNCATE, leitura de auth.accounts e SET ROLE migration_owner. Ver SQL-02/03 e os JSON da execução, cujo perfil está explicitado no relatório.

**Limitação ou risco residual.** O proprietário e o administrador conservam poderes elevados. O comprometimento integral do backend também pode atingir suas duas credenciais; a separação reduz permissões, mas não cria uma fronteira física entre os processos.

**Revisão individual do aluno:** pendente. Nome/RA e ajustes: ____________________.

## 2. Considere que o PostgreSQL foi instalado em um servidor interno. Descreva como pg_hba.conf, firewall, SCRAM e TLS trabalham juntos para reduzir o risco de acesso indevido ao banco.

**Conceito.** Firewall restringe alcance da porta; pg_hba define origem, usuário, base e método; SCRAM autentica por desafio/resposta; TLS cifra o tráfego e permite verificar o servidor.

**Risco.** Uma senha forte não impede alcance indevido da rede nem interceptação se o cliente não validar certificado e hostname. TLS não limita o que um usuário autenticado pode consultar.

**Configuração implementada.** O Compose define rede interna sem portas dos bancos publicadas. Regras hostssl aceitam apenas as identidades/bases previstas na subnet de dados e rejeitam plaintext e demais origens. password_encryption usa scram-sha-256; psycopg usa verify-full e CA local. O perfil nativo troca a subnet por loopback.

**Evidência observável.** `test_sql_authentication` confere verificador SCRAM e credencial inválida; `test_sql_tls` observa pg_stat_ssl e nega plaintext/hostname errado. ENV-01 inspeciona Docker efetivo quando disponível. Nesta entrega, a execução nativa não comprova a regra de uma origem estrangeira de rede de contêineres.

**Limitação ou risco residual.** Firewall real do host e alcance a partir de uma rede externa não foram certificados nesta execução. A CA é didática e seus 90 dias de validade exigem renovação planejada.

**Revisão individual do aluno:** pendente. Nome/RA e ajustes: ____________________.

## 3. No cenário multiempresa, explique como Row-Level Security ajuda a impedir que um usuário de uma empresa consulte pedidos de outra. Indique também uma limitação do uso de RLS.

**Conceito.** RLS restringe as linhas visíveis e graváveis no SGBD, mesmo quando uma consulta da aplicação não contém WHERE de tenant.

**Risco.** Confiar em tenant_id do navegador permitiria forjar contexto. Políticas somente de leitura também deixariam lacunas de inserção ou atualização.

**Configuração implementada.** Tenants, customers e orders têm ENABLE/FORCE RLS e políticas USING/WITH CHECK. O backend obtém tenant da conta autenticada e executa set_config com is_local=true na transação. A FK composta liga cliente e pedido na mesma empresa. A conta runtime não é proprietária nem tem BYPASSRLS.

**Evidência observável.** `test_sql_rls_direct` observa leitura vazia, UPDATE de zero linhas e INSERT negado no contexto A contra B. `test_api_tenant_access` e `test_api_write_scope` verificam IDs/URLs, criação e alteração. `test_sql_context_reset` reutiliza a conexão após commit e confirma ausência de contexto remanescente.

**Limitação ou risco residual.** O GUC de contexto pode ser alterado por quem já controla a sessão SQL; logo, não protege de um backend comprometido ou de SQL arbitrário. Superusers/BYPASSRLS continuam fora da proteção. RLS não substitui revisão de views, funções e privilégios globais.

**Revisão individual do aluno:** pendente. Nome/RA e ajustes: ____________________.

## 4. Explique por que prepared statements são essenciais mesmo quando a aplicação já valida campos do formulário. Use um exemplo do laboratório para diferenciar validação de entrada e parametrização.

**Conceito.** Validação confirma formato, tipo, faixa e regra de negócio. Parametrização mantém dados separados da estrutura do comando SQL.

**Risco.** Entradas válidas como texto ainda podem conter aspas ou trechos semelhantes a comandos. A concatenação permitiria que dados mudassem a lógica da consulta.

**Configuração implementada.** A pesquisa de clientes usa ILIKE com placeholder %s e tupla de parâmetros; o driver executa com prepare=True. Pedidos têm UUID, limite de texto e Decimal positivo com duas casas. Não se interpola entrada na sintaxe SQL.

**Evidência observável.** `test_sql_injection` envia uma busca legítima e a string adversarial inofensiva com aspas/OR. A segunda retorna zero resultados, mantendo o filtro de tenant e tratando a entrada como dado. `test_api_validation` recusa mass assignment de tenant_id e tipos indevidos.

**Limitação ou risco residual.** Validação e parametrização não concedem autorização. Identificadores SQL dinâmicos, quando necessários na operação de restore, usam psycopg.sql.Identifier e uma allowlist de tabelas; não placeholders de valores.

**Revisão individual do aluno:** pendente. Nome/RA e ajustes: ____________________.

## 5. Proponha um conjunto mínimo de logs, alertas e evidências de backup/restore que deveriam ser mantidos para demonstrar segurança e capacidade de recuperação do banco SQL.

**Conceito.** Auditoria registra quem fez o quê e quando; continuidade exige cópia recuperável e evidência de restauração, não apenas um comando de dump concluído.

**Risco.** Sem logs de login/DDL/privilégios e eventos críticos, uma alteração pode passar sem atribuição. Backup não testado pode falhar quando necessário.

**Configuração implementada.** Logs nativos registram conexão/desconexão e DDL; a API grava eventos estruturados sem corpo/token/senha; um trigger SQL registra ator, operação, tenant e pedido. O dump usa snapshot exportado e a cópia mantida usa AES-256-GCM. Restore cria uma base com prefixo protegido e nome novo.

**Evidência observável.** `test_sql_audit` verifica INSERT do pedido na trilha e presença real de conexão, DDL e falha de autenticação no log, exportando somente flags sanitizadas. `test_sql_backup` compara contagens e fingerprints de tenants/customers/orders após restauração, registrando duração.

**Limitação ou risco residual.** Não há SIEM/alertas automáticos/retencão imutável. Proponho alertas de falhas repetidas de autenticação, mudanças de privilégios, falha de backup e atraso de restore test. A cópia local e a chave no mesmo host não satisfazem recuperação de desastre; RTO/RPO precisam de requisitos e operação contínua.

**Revisão individual do aluno:** pendente. Nome/RA e ajustes: ____________________.

## 6. Explique a diferença entre a conta administrativa e a conta da aplicação. Quais riscos surgem quando a aplicação recebe permissões além das necessárias?

**Conceito.** A conta administrativa gerencia identidades, esquemas e tarefas operacionais; a conta da aplicação executa o caso de uso dentro de privilégios delimitados.

**Risco.** Uma API com root ou privilégio de mudar validadores pode criar usuários, neutralizar controles e ampliar o alcance de um vazamento.

**Configuração implementada.** `lab_admin` tem papel root para bootstrap e operações isoladas, fora da API. `api_user` autentica em lab e herda catalog_api, com find/insert/update apenas em products/profiles. Não tem remove, createUser, collMod ou bypassDocumentValidation.

**Evidência observável.** `test_mongo_admin_separation` observa connectionStatus e identidade distinta. `test_mongo_rbac` aceita leitura e recusa usersInfo administrativo, createUser, collMod e escrita em coleção não concedida com código 13.

**Limitação ou risco residual.** O acesso da aplicação cobre documentos de duas empresas e a fronteira entre elas é implementada no servidor. RBAC por coleção não equivale a isolamento por linha/documento de tenant.

**Revisão individual do aluno:** pendente. Nome/RA e ajustes: ____________________.

## 7. Considere uma API que aceite filtros MongoDB enviados diretamente pelo cliente. Explique como operadores como $ne ou $where podem ser abusados e como a aplicação deve validar os filtros.

**Conceito.** Operadores MongoDB são parte da linguagem de consulta. Aceitar o objeto do cliente como filtro permite que ele determine a semântica da busca.

**Risco.** $ne pode ampliar igualdade para desigualdade; $where pode introduzir expressões de JavaScript em configurações que o habilitem. Repassar JSON arbitrário cria uma superfície além dos filtros de produto previstos.

**Configuração implementada.** CatalogQuery só aceita q, category e limit, com extra=forbid, enum e limites. Objetos e caracteres de operador não são aceitos no texto. O servidor monta tenant_id a partir da sessão e usa re.escape para a busca literal. JavaScript server-side está desabilitado na configuração.

**Evidência observável.** `test_mongo_injection` e `test_api_validation` rejeitam q[$ne], $where, JSON indevido e objeto no preço com HTTP 422. A busca por metacaracteres .* não amplia os resultados. A escrita/consulta entre empresas também é verificada pela API.

**Limitação ou risco residual.** A defesa depende de todos os caminhos usarem a construção de filtros revisada. Índices, limites e autorização continuam necessários para desempenho e proteção de dados; bloquear um caractere sozinho não é uma solução geral.

**Revisão individual do aluno:** pendente. Nome/RA e ajustes: ____________________.

## 8. Por que utilizar JSON Schema em um banco orientado a documentos considerado flexível? Relacione a resposta com integridade, qualidade dos dados e segurança.

**Conceito.** Flexibilidade documental permite evolução, mas não elimina invariantes de integridade e de segurança. JSON Schema estabelece contrato no ponto persistente.

**Risco.** Sem um contrato, preços negativos, tipos incorretos ou campos inesperados podem quebrar regras de negócio, gerar interpretações divergentes e contaminar os dados.

**Configuração implementada.** Produtos e perfis têm $jsonSchema strict/error com campos obrigatórios, tipos BSON, faixas, enumerações e additionalProperties=false. _id e tenant_id têm formato previsto; índices únicos reforçam SKU/e-mail por empresa. A API possui validação adicional com Pydantic.

**Evidência observável.** `test_mongo_schema` grava diretamente via PyMongo, sem passar pelo formulário/Pydantic: produto/perfil válido é aceito e documento inválido é recusado pelo MongoDB com código 121. Assim se distingue uma rejeição do SGBD de uma rejeição apenas na interface.

**Limitação ou risco residual.** Esquema não verifica veracidade, autorização de tenant nem finalidade de uso dos dados. Migrações e evolução do contrato precisam de revisão e teste de compatibilidade.

**Revisão individual do aluno:** pendente. Nome/RA e ajustes: ____________________.

## 9. Descreva como bindIp, firewall e TLS se complementam para proteger o MongoDB. Explique por que criptografia em trânsito não substitui controle de rede.

**Conceito.** bindIp seleciona interfaces de escuta; firewall/segmentação limitam origens; TLS protege confidencialidade/integridade do canal e verifica o endpoint.

**Risco.** Um endpoint público com TLS ainda aceita tentativas de autenticação de origens indesejadas. Criptografar tráfego não reduz por si só a superfície de rede.

**Configuração implementada.** Dentro do Compose, MongoDB escuta em 0.0.0.0 para atender API/ops na rede interna; não publica porta e exige TLS. O perfil nativo escuta exclusivamente em 127.0.0.1. PyMongo verifica CA/hostname, sem flags para aceitar certificado inválido.

**Evidência observável.** `test_mongo_network` observa getCmdLineOpts do servidor. `test_mongo_tls` aceita canal verificado e recusa plaintext, CA não confiável e hostname errado. ENV-01 é necessário para comprovar a ausência de publicação no Compose; não foi executado com o motor Docker indisponível.

**Limitação ou risco residual.** A configuração declarada de rede deve ser confrontada com o ambiente efetivo. O teste nativo de loopback não certifica firewall externo, roteadores ou regras de produção.

**Revisão individual do aluno:** pendente. Nome/RA e ajustes: ____________________.

## 10. Após concluir o laboratório NoSQL, identifique três riscos que ainda podem permanecer mesmo com autenticação, TLS, RBAC e backup configurados. Proponha controles adicionais.

**Conceito.** Risco residual é a exposição que persiste depois dos controles, considerando seu alcance, o processo operacional e ameaças ainda plausíveis.

**Risco.** Três riscos permanecem: credencial/host comprometido; cópia e chave perdidas no mesmo domínio de falha; dependência ou configuração vulnerável após a entrega.

**Configuração implementada.** O laboratório usa conta limitada, TLS, validação e dump cifrado/restauração isolada. As medidas adicionais propostas são, respectivamente: MFA/PAM e rotação/cofre; offsite/imutabilidade e agenda/PITR apropriado; patching, SCA contínua, revisão de migrations e alertas.

**Evidência observável.** A tabela versionada em docs/riscos_residuais.md liga risco, impacto, controle e próxima medida. NOSQL-09 registra restore e igualdade de dados; as auditorias de dependências têm relatórios próprios com a data. Propostas não são registradas como controles existentes.

**Limitação ou risco residual.** A execução em standalone exige cuidado com consistência durante escritas. Não há evidência de HA, disaster recovery completo ou cumprimento de RTO/RPO de negócio; esses pontos não podem receber pontuação fictícia nos simuladores.

**Revisão individual do aluno:** pendente. Nome/RA e ajustes: ____________________.
