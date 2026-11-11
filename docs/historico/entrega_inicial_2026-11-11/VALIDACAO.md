# Validação observada - 11/11/2026

## Resultado

- **33 testes pytest aprovados**, com PostgreSQL 17.6 e MongoDB Community 8.0 reais em Windows nativo. A suíte executou a API FastAPI em processo e os drivers sobre conexões TLS reais, sem simular SGBDs.
- **3 testes de interface aprovados** com Vitest/React Testing Library, TypeScript compilado e build Vite concluído. Os testes unitários de UI não são usados como prova de TLS/RLS/RBAC.
- `npm audit` e `pip-audit -r requirements.txt` não encontraram vulnerabilidades conhecidas no momento da consulta. Os resultados estão em `evidencias/npm-audit.json` e `evidencias/python-audit.json`; não são garantia futura nem varredura das imagens Docker.
- `docker compose config --quiet` aprovou a sintaxe/configuração resolvida. **O motor Docker não iniciou**, por erro interno de socket do Docker Desktop. A topologia efetiva e os builds de contêiner permanecem sem validação dinâmica; ENV-01 não foi fabricado.
- O painel apresenta **17 controles comprovados e 3 pendentes**: SQL-01, NOSQL-01 e NOSQL-05 aguardam ENV-01. A comprovação dos demais se limita ao perfil nativo registrado em cada relatório.

## Comando efetivamente usado na integração

PowerShell, a partir da raiz do projeto, com o ambiente virtual de trabalho e os executáveis oficiais disponíveis no PATH:

```powershell
$env:LAB_INTEGRATION="1"
$env:LAB_TEST_ENV="Windows nativo / bancos reais / TLS verificado / Compose não executado"
python -m pytest tests -q --tb=short
```

O PATH incluiu pg_dump/pg_restore 17.6 e MongoDB Database Tools 100.13.0. A inicialização real utilizou `scripts/native.py start --pg-bin <diretório dos binários portáteis>`, com o mongod instalado em `C:\Program Files\MongoDB\Server\8.0\bin\mongod.exe`. Os caminhos absolutos particulares não são exigências para outro computador. As versões efetivas constam no JSON de ambiente.

## O que foi observado

Login válido/inválido, acesso sem sessão, papel de leitura, CSRF, origem HTTP recusada, RLS direto e via API em leitura/inserção/alteração, reset transacional de tenant, parametrização SQL, roles e operações administrativas negadas, TLS válido/plaintext/hostname incorreto, fonte loopback 127.0.0.2 rejeitada pelo pg_hba antes da senha, MongoDB anônimo negado, RBAC por coleção, escrita válida e inválida diretamente no MongoDB, filtro de operador recusado, eventos sanitizados e restore em bases distintas com contagens/fingerprints iguais. Backups foram cifrados com AES-256-GCM e decriptados da cópia salva para o restore.

Tempos e contagens variam entre execuções porque a suíte acrescenta registros sintéticos identificáveis. Os hashes e métricas do relatório representam a execução que os produziu, não uma igualdade perpétua com a base após novas operações na interface. Os bancos restaurados são preservados para inspeção; não há limpeza destrutiva automática.

## Revisão visual e correções

Foram observados login A/B/leitor, dados distintos na empresa B, criação/aprovação de pedido, gravação de produto, filtros de controles pendentes, dez questões renderizadas, eventos reais e fechamento de diálogo por Escape. Larguras CSS de **320, 768, 1440 e 2560 px** foram verificadas. Um overflow de tabela causado por texto de acessibilidade sem ancestral posicionado foi corrigido e rechecado; tabelas permanecem com rolagem interna. A navegação compacta recebeu nomes acessíveis explícitos.

A amostra de contraste dos textos visíveis do painel não apresentou candidatos abaixo do limiar calculado após ajustes. Não houve auditoria WCAG completa ou avaliação de todas as combinações de tecnologias assistivas. O manifesto visual registra alcance e limitações. Capturas são JPEGs reais de navegador, sem montagem de dados ou métricas.

Foi corrigida a codificação UTF-8 da carga psql no Windows. O teste de ambiente verifica o nome sintético com acento no banco. A revisão estática adicional corrigiu a preparação de ownership do volume de auditoria do Compose e a cópia da configuração npm antes de npm ci; essas correções de contêiner ainda dependem de execução no motor Docker.

O PDF foi gerado da fonte Markdown versionada, renderizado com Poppler e inspecionado visualmente. Nomes/RA continuam como campos a preencher. As respostas exigem revisão individual do aluno; os simuladores aguardam coleta humana. Nenhuma execução de CI remota ou publicação no GitHub foi alegada.

## Aviso de compatibilidade observado

A suíte passou com um aviso de depreciação do TestClient de Starlette referente ao uso de httpx. Não houve falha funcional. A dependência foi mantida no ambiente verificado; uma futura migração para o sucessor indicado deve passar pela mesma suíte.
