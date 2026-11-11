# Validação atual - revisão e instalação em Documents (11/11/2026)

> Preparação posterior: README Windows/macOS e iniciador PowerShell 5.1 conferidos; 30 verificações do iniciador (Docker simulado) e 19 testes unitários Python aprovados. Veja [PREPARACAO_PUBLICACAO.md](PREPARACAO_PUBLICACAO.md). O estado histórico abaixo não equivale ao estado remoto atual.

> Revisão posterior de distribuição: suíte nativa com 46 PASS e 1 SKIP Docker; recorte unitário final 19 PASS; 5 testes de interface e build aprovados. As contagens se sobrepõem. Veja [REVISAO_DOCKER_MACOS.md](REVISAO_DOCKER_MACOS.md). O PDF e os resultados de 39 testes descritos abaixo pertencem à revisão anterior preservada.

A instalação principal é `C:\Users\Guilherme\Documents\SecureDB-Lab`. O atalho **SecureDB Lab** na Área de Trabalho aponta para o Python desse ambiente e para `scripts/desktop.py` nessa pasta.

## Testes observados

- **39 testes Python: PASS; 0 FAIL; 0 SKIP**. A execução incluiu PostgreSQL 17.6, MongoDB Community 8.0.8, TLS real, RLS, RBAC, schema, filtros, backup/restore e smoke HTTP do inicializador.
- **5 testes de interface: PASS**; TypeScript e build Vite aprovados dentro da pasta definitiva.
- O smoke do desktop verificou a identidade da instalação, health dos bancos/API, MIME do JavaScript compilado, login/logout com cookie HttpOnly pelo proxy, origem indevida negada, pesquisa de perfis, exportação e os detalhes dos vinte controles. Listagem de diretórios recebeu 403 e tentativa de acessar arquivo privado recebeu 404.
- O atalho real foi executado. A primeira verificação de reabertura identificou uma corrida entre um marcador de parada antigo e o polling da janela. O marcador agora é limpo antes da criação da GUI; o teste de regressão e a reabertura real foram observados. O serviço permaneceu em estado ready após a abertura pelo atalho.
- `docker compose config --quiet` e a verificação de segredos nos arquivos publicáveis passaram. O Docker Desktop continua sem motor disponível; **a execução dos contêineres não foi observada**.

## Lacunas corrigidas nesta revisão

1. Pesquisa de perfis por nome/e-mail e segmento, com parâmetros tipados, regex literal e tenant da sessão; operadores e campos extras rejeitados.
2. Objetivo, cenário positivo, cenário negativo e excerto de arquivo real para cada um dos vinte controles. Um teste confere que os excertos correspondem à fonte versionada e que não apontam para `.local` ou `.env`.
3. Perfil Docker explicitado nos metadados das futuras execuções. ENV-01 entra na exportação apenas quando a suíte é do perfil Docker; não contamina uma execução nativa posterior.
4. Expiração de sessão devolve a interface ao login; progress usa HTML nativo, compatível com a política sem estilos inline.
5. Uso do atalho, manutenção de caches, encerramento e procedimento separado de reinicialização de dados documentados.
6. Código, dados, dependências locais, binários e três materiais originais reunidos na pasta principal, sem dependência ativa da antiga pasta work do Codex.

## Reprodução desta suíte

Com o inicializador aberto, na raiz da instalação:

```powershell
$env:LAB_INTEGRATION="1"
$env:LAB_DESKTOP_HTTP="1"
$env:LAB_TEST_ENV="Windows nativo / Documents SecureDB-Lab / atalho e HTTP reais / TLS verificado / Compose não executado"
$env:PATH="$PWD\.local\tools\postgres\bin;$PWD\.local\tools\mongodb-tools\bin;"+$env:PATH
.venv\Scripts\python -m pytest tests -q --tb=short
```

O smoke desktop é opcional fora desse perfil: sem `LAB_DESKTOP_HTTP=1`, ele será SKIP, explicitamente. Não se deve tratar essa omissão como PASS.

## Evidências e limites

A evidência atual está em `evidencias/entrega/revisao_2026-11-11/` e no relatório ativo `evidencias/latest.json`. A entrega inicial de 33 testes Python e 3 de interface foi preservada em `docs/historico/entrega_inicial_2026-11-11/` e nas evidências iniciais. As capturas anteriores de responsividade e a amostra de contraste permanecem válidas para o escopo registrado; esta revisão acrescenta conferência funcional de pesquisa e detalhes no navegador.

O painel continua com **17/20 controles comprovados** no perfil nativo. SQL-01, NOSQL-01 e NOSQL-05 aguardam ENV-01 da implantação real em Docker. Coleta dos simuladores, revisão individual das respostas e integrantes/RA continuam pendentes. Não há publicação GitHub ou CI remota realizada.

Os tempos e fingerprints de backup pertencem à execução que os gerou. Novos testes acrescentam dados sintéticos. O restore ocorre em bases separadas e os dumps mantidos são cifrados. A suíte passou com um aviso de depreciação do TestClient/httpx, sem falha funcional. As auditorias de dependências da entrega inicial foram preservadas; não equivalem a uma auditoria das versões dos servidores ou das imagens não iniciadas.
