# SecureDB Lab

Aplicação acadêmica local para os laboratórios FACAMP de Segurança da Informação e Cibersegurança em Bancos de Dados. Pedidos multiempresa em PostgreSQL; catálogo/perfis em MongoDB Community; React e FastAPI; painel que apresenta evidências reais de CLI.

**Estado da entrega:** consulte [validação](docs/VALIDACAO.md), [rastreabilidade](docs/rastreabilidade.md) e [relatório](docs/relatorio_final.pdf). Os bancos/API foram testados em Windows nativo com TLS verificado. O motor Docker local falhou ao iniciar; a execução efetiva do Compose permanece pendente. Simuladores aguardam coleta humana. Nenhum resultado dessa lacuna foi fabricado.

## Início com Docker (fluxo principal reproduzível)

Pré-requisitos: Docker Engine/Desktop com contêineres Linux e Compose v2, Git, Python 3.11+ (3.12 nos contêineres), aproximadamente 4 GB livres de RAM e porta local 8080. Node 22.14+ somente para desenvolvimento do frontend; a imagem de build usa Node 22.20. Os bancos não publicam portas. A subnet 172.29.74.0/24 deve estar disponível.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python scripts/lab.py setup
.venv\Scripts\python scripts/lab.py up
```

Linux/macOS: substitua `.venv\Scripts\python` por `.venv/bin/python`. Abra **http://localhost:8080**. As senhas são geradas em `.local/ACESSO_LOCAL.txt` e nunca publicadas. Usuários: `aurora.editor` (A), `vertice.editor` (B), `aurora.leitor` (somente leitura na A). Não existe seletor de tenant enviado pelo frontend.

```powershell
python scripts/lab.py seed
python scripts/lab.py test
python scripts/lab.py backup --database both
python scripts/lab.py restore --database both
python scripts/lab.py report
python scripts/lab.py diagnose
python scripts/lab.py preflight
python scripts/lab.py stop
```

Use o Python do ambiente virtual ativado nesses comandos. `up` aguarda readiness, inicializa dados idempotentes e inspeciona rede/portas. `stop` preserva volumes. `backup` e `restore` executam uma volta completa de dump cifrado/restauração em destino novo: não restauram sobre a origem. Destinos `restore_pg_<uuid>` e `restore_mongo_<uuid>` são preservados para inspeção e consomem espaço a cada execução. Nenhuma limpeza destrutiva automática é oferecida.

Os backups permanecem cifrados em `.local/backups`; a chave está em `.local/admin/backup.key`. Preserve-a separadamente antes de mover o ambiente. Em MongoDB standalone, pause escritas durante o dump; a comparação antes/depois não cria consistência transacional.

## Desenvolvimento e alternativa nativa Windows

Para usar PostgreSQL portátil 17.x e MongoDB Community 8.0.x instalados pelo aluno, sem instalar serviços do sistema:

```powershell
python scripts/native.py start --pg-bin "C:\ferramentas\pgsql\bin" --mongod "C:\Program Files\MongoDB\Server\8.0\bin\mongod.exe"
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --no-access-log
```

Em outro terminal, dentro de `web`:

```powershell
npm ci
npm run dev
```

Abra **http://127.0.0.1:5173**. Vite encaminha `/api` ao backend. A alternativa nativa cria dados somente em `.local/native`, usa portas 55432/57017 em loopback e a mesma CA/verificação TLS. Ela **não valida a rede de contêineres**. A instalação do MongoDB existente é usada como binário, sem alterar seu serviço/configuração original.

Para integração nativa, disponibilize `pg_dump`, `pg_restore`, `mongodump` e `mongorestore` no PATH e execute:

```powershell
$env:LAB_INTEGRATION="1"
$env:LAB_TEST_ENV="Windows nativo / bancos reais / TLS verificado / Compose não executado"
python -m pytest tests -q
```

O arquivo `.local/runtime.json` serve ao perfil nativo. Os contêineres usam `.local/runtime/runtime.json`. Não troque seus segredos ou mounts. Para parar os bancos nativos: `python scripts/native.py stop --pg-bin "C:\ferramentas\pgsql\bin"`; encerre também os processos locais Vite/Uvicorn que iniciou.

## Testes e evidências

```powershell
python -m pytest tests/test_unit.py
cd web
npm test
npm run build
npm audit
```

Os testes unitários do frontend usam respostas controladas para verificar estados de UI; não comprovam controles de SGBD. A integração usa drivers reais, Pydantic e endpoints reais, sem bancos simulados. Cada teste registra ID, objetivo, controles, PASS/FAIL/SKIP, data, observação sanitizada e caminho. `evidencias/latest.json` é a fonte do painel. Para um controle ser aprovado, **todos** os testes requeridos precisam de PASS. ENV-01 só é produzido após inspeção efetiva do Docker.

Arquivos gerados de testes são ignorados por padrão. Uma cópia sanitizada desta execução acompanha `evidencias/entrega/`, com hashes no manifesto de entrega. Ao clonar, o painel começa pendente até rodar a própria suíte; o histórico entregue não é importado como comprovação do novo ambiente.

## Segurança e escopo

Sessões HttpOnly/SameSite Strict, CSRF e Origin; Argon2id; autorização por papel; RLS com FORCE/USING/WITH CHECK; FK composta; SQL parametrizado; TLS verificando CA/hostname; RBAC MongoDB por coleção; `$jsonSchema` strict/error; filtros tipados; auditoria sanitizada e backups AES-256-GCM. Não há endpoint de execução de comandos administrativos.

HTTP/cookie sem Secure é restrito ao navegador local. Não expor este laboratório à Internet. Consulte [riscos residuais](docs/riscos_residuais.md): ausência de MFA/HA/SIEM/offsite, limites de RLS baseado em contexto confiável e isolamento MongoDB na API. As imagens têm tags de versão fixadas, não digests; os clientes administrativos instalados pelo Dockerfile ops são resolvidos nos repositórios oficiais no build e suas versões devem ser registradas na execução final.

O npm instalado apresentou falha de resolução de peers ao atualizar Vitest; `.npmrc` fixa `legacy-peer-deps=true` e os peers efetivamente usados nos testes são declarados explicitamente. `npm ci`, testes e build foram verificados com o lockfile entregue.

## Documentos e publicação futura

Veja `docs/arquitetura.md`, `docs/inventario_controles.md`, `docs/questoes_dissertativas.md`, `docs/simuladores.md`, `docs/riscos_residuais.md`, `docs/relatorio_final.md` e o PDF. Preencha nomes/RA, revise as respostas individualmente e faça a coleta dos simuladores. Os materiais originais FACAMP não são redistribuídos automaticamente.

Git local está inicializado na branch main, sem remote. [Guia para GitHub](docs/github.md), workflows de CI, Dependabot, template de PR e `SECURITY.md` estão prontos. Publicação/remote ficam para o senhor criar depois; nenhuma conta ou repositório remoto foi criado nesta entrega.
