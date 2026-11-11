# Evidências da execução local no Mac

Execução de 11/11/2026, Docker Compose no macOS Apple Silicon. A seleção local passou em 28 verificações. ENV-01 é uma verificação adicional da topologia, registrada na inicialização.

- `resultado_integrado.json` registra os testes selecionados e as observações de cada cenário.
- `environment.json` registra os dois bancos em rede interna, sem portas publicadas.
- `sql-pedidos-aurora.png` e `sql-pedidos-vertice.png` mostram as telas das duas contas. A confirmação do bloqueio está nos testes `test_api_tenant_access` e `test_sql_rls_direct`.
- `nosql-catalogo.png` e `nosql-perfis.png` mostram os dados sintéticos na interface. Os testes `test_mongo_schema` e `test_api_mongo_tenant_and_crud` comprovam as verificações do banco e da API.
- Os testes `test_sql_backup` e `test_mongo_backup` incluem tempos, contagens e fingerprints da origem e dos destinos restaurados. As cópias cifradas ficam na instalação local.
- Quatro controles ainda dependem de verificações que ficaram fora desta seleção: SQL-07, SQL-10, NOSQL-08 e NOSQL-10. As evidências históricas permanecem no repositório.
