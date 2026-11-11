# Uso pelo atalho da Área de Trabalho

A instalação principal deste computador fica em `C:\Users\Guilherme\Documents\SecureDB-Lab`. O atalho **SecureDB Lab** executa o inicializador dessa pasta. Não depende mais da pasta temporária `Codex\...\work`.

O inicializador confirma que as portas não pertencem a outro ambiente, prepara os caminhos locais sem trocar credenciais, inicia PostgreSQL e MongoDB com TLS, aguarda a API e serve o build React em `http://127.0.0.1:5173`. O painel pequeno permite abrir a aplicação, consultar os acessos sintéticos e encerrar o laboratório. Um segundo clique reaproveita a instância já aberta.

Todos os arquivos específicos do projeto ficam nesta subpasta:

- Código, Git local, documentação, testes e evidências: raiz e subdiretórios versionáveis.
- Ambiente Python: `.venv/`.
- PostgreSQL, mongod e ferramentas de dump/restore: `.local/tools/`.
- Dados, certificados, credenciais, cópias cifradas e logs: `.local/` (ignorada no Git).
- Três materiais originais da disciplina: `.local/referencias/` (cópias privadas, sem redistribuição automática no Git).
- Interface compilada usada pelo atalho: `web/dist/`.

Python do Windows continua sendo um pré-requisito do sistema; Node/npm são necessários apenas para desenvolver ou recompilar o frontend. Não há instalação de serviço do Windows nem alteração do MongoDB que já existia em Program Files.

## Operações locais

```powershell
.venv\Scripts\python scripts/desktop.py start
.venv\Scripts\python scripts/desktop.py status
.venv\Scripts\python scripts/desktop.py stop
```

Ao fechar o painel, os serviços desta instalação são encerrados e seus dados são preservados. Se uma porta estiver ocupada por outra instalação, o inicializador recusa a operação em vez de matar processos externos. Erros ficam em `.local/desktop/startup.log`, que não deve ser publicado.

## Limpeza e reinicialização

```powershell
.venv\Scripts\python scripts/maintenance.py clean
.venv\Scripts\python scripts/maintenance.py clean --apply
```

O primeiro comando só mostra os caches regeneráveis; `--apply` remove apenas os diretórios de cache permitidos dentro do projeto. Bancos, backups, evidências e certificados não são selecionados. Não execute limpeza durante uma suíte de testes.

Uma reinicialização integral de dados é uma ação separada e destrutiva, não executada nesta entrega. Preserve um backup cifrado **e a chave** e confirme o restore antes. No Compose, o comando explícito `docker compose down --volumes` remove os volumes SQL, NoSQL e auditoria desse projeto; só deve ser escolhido conscientemente pelo aluno. No perfil nativo, prefira instalar uma nova cópia em outra pasta com portas distintas; não apague `.local` para resolver erros de inicialização.

Após clonar o código em outro computador, instale dependências e use o fluxo Compose do README, ou prepare as ferramentas nativas na estrutura indicada. O atalho e as dependências locais desta máquina não são incluídos no ZIP público nem no Git.
