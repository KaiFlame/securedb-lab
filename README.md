# SecureDB Lab

Aplicação local para estudar e demonstrar segurança em bancos de dados. O laboratório reúne pedidos multiempresa em PostgreSQL, catálogo e perfis em MongoDB Community, login e um painel com vinte controles e suas evidências.

**Para usar o ZIP, instale apenas o Docker Desktop. Python, Node e Git não são necessários no computador.** A primeira inicialização precisa de Internet para obter e construir as dependências.

## 1. Baixe o projeto

Abra [KaiFlame/securedb-lab](https://github.com/KaiFlame/securedb-lab), clique no botão **Code** e escolha **Download ZIP**. Extraia o arquivo inteiro para uma pasta do seu computador. No Windows, use **Extrair tudo**; no Mac, abra o ZIP pelo Finder.

Entre na pasta extraída que contém este `README.md`, `docker-compose.yml`, `iniciar.cmd` e `iniciar.command`. Execute os iniciadores dessa pasta; não os abra de dentro do ZIP nem copie apenas um deles para outro lugar.

Quem já usa Git pode baixar assim:

```sh
git clone https://github.com/KaiFlame/securedb-lab.git
cd securedb-lab
```

Baixar ou clonar traz o código e as evidências públicas. Os bancos atuais, as senhas e os dados privados de outra instalação não são copiados. A sua primeira execução prepara um ambiente local próprio.

## 2. Prepare o Docker Desktop

| Sistema | Preparação |
|---|---|
| **Windows** | Instale o [Docker Desktop oficial para Windows](https://docs.docker.com/desktop/setup/install/windows-install/). Use contêineres **Linux** e siga a preparação de WSL 2 indicada pelo Docker. Reinicie o Windows se o instalador solicitar. Depois abra o Docker Desktop pelo menu Iniciar. |
| **macOS** | Instale o [Docker Desktop oficial para Mac](https://docs.docker.com/desktop/setup/install/mac-install/), escolhendo **Apple Silicon** ou **Intel** conforme **Sobre Este Mac**. Abra o Docker em Aplicativos. |

Conclua a primeira abertura, leia e aceite os termos se concordar e aguarde o motor ficar em execução. O laboratório não instala o Docker nem aceita esses termos por você. Guias detalhados: [Windows](docs/instalacao_windows.md) e [macOS](docs/instalacao_macos.md).

## 3. Inicie e entre

Com o Docker Desktop aberto, dê duplo clique no arquivo correspondente:

| Ação | Windows | macOS |
|---|---|---|
| Iniciar | `iniciar.cmd` | `iniciar.command` |
| Executar testes | `testar.cmd` | `testar.command` |
| Parar preservando dados | `parar.cmd` | `parar.command` |

Na primeira vez, acompanhe a janela até terminar o download, o build e a preparação dos serviços. As próximas aberturas reaproveitam os dados. O bootstrap gera credenciais e certificados; o serviço de seed cria as contas de demonstração. Não é necessário cadastrar usuários ou instalar os bancos manualmente.

Quando a inicialização terminar, abra **[http://localhost:8080](http://localhost:8080)** no navegador do mesmo computador. Se o navegador não abrir sozinho, use esse endereço.

### Onde está a senha?

Abra `.local/ACESSO_LOCAL.txt`, dentro da pasta do projeto. No Finder, `Command + Shift + .` mostra os arquivos e diretórios que começam com ponto. Esse arquivo é criado localmente e não está no GitHub.

| Usuário | Empresa | Permissão |
|---|---|---|
| `aurora.editor` | A — Aurora Comércio | Consultar e alterar dados da própria empresa |
| `vertice.editor` | B — Vértice Tecnologia | Consultar e alterar dados da própria empresa |
| `aurora.leitor` | A — Aurora Comércio | Somente leitura |

As senhas são geradas para cada instalação. Não há uma senha pública padrão. Para trocar de empresa, saia da sessão e entre com a outra identidade: a empresa é definida pelo backend, sem seletor de tenant no formulário.

Também é possível consultar os acessos pelo terminal, conforme os comandos abaixo. Guarde essa saída localmente; não a inclua em prints ou mensagens públicas.

## 4. Explore o laboratório

- **Pedidos SQL:** liste, crie e atualize pedidos; entre como A e depois B para observar dados separados.
- **Catálogo e perfis:** pesquise, cadastre e edite documentos sintéticos sujeitos a filtros tipados e validação do MongoDB.
- **Controles e evidências:** filtre os vinte controles e consulte objetivo, configuração, testes e riscos residuais.
- **Documentação:** leia o roteiro dos laboratórios, as dez questões e o relatório técnico.

O botão de atualizar evidências apenas consulta relatórios. Para produzir novos resultados, execute a suíte pelo iniciador de testes ou pela CLI. Um clique no painel não aprova um controle.

## Comandos pelo terminal

Abra o terminal **na pasta que contém este README**. No Windows, pode digitar `powershell` na barra de endereço do Explorador de Arquivos e pressionar Enter. No Mac, use o Terminal e entre na pasta extraída com `cd`.

### Windows — PowerShell

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\docker.ps1 up
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\docker.ps1 credentials
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\docker.ps1 test
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\docker.ps1 diagnose
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\docker.ps1 backup -Database both
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\docker.ps1 restore -Database both
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\docker.ps1 report
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\docker.ps1 down
```

`-ExecutionPolicy Bypass` vale para esse processo do PowerShell; não altera a política permanente do computador. Os arquivos `.cmd` usam esse inicializador.

### macOS ou Linux — shell

```sh
sh scripts/docker.sh up
sh scripts/docker.sh credentials
sh scripts/docker.sh test
sh scripts/docker.sh diagnose
sh scripts/docker.sh backup --database both
sh scripts/docker.sh restore --database both
sh scripts/docker.sh report
sh scripts/docker.sh down
```

No Mac, se o duplo clique nos `.command` não funcionar após a extração, use os comandos do Terminal. Para dar permissão executável aos iniciadores:

```sh
chmod +x iniciar.command parar.command testar.command
```

`test` usa bancos reais, pode acrescentar dados sintéticos e produz evidências. `diagnose` inspeciona os contêineres e a rede efetivos. `report` gera o relatório a partir das fontes e dos resultados disponíveis. Falhas e testes `SKIP` permanecem explícitos.

## Parar, reabrir e preservar dados

Use `parar.cmd`, `parar.command` ou o comando `down`. Fechar a aba do navegador não encerra os serviços. A parada normal **preserva os volumes dos bancos, as credenciais e os arquivos locais**; volte a executar o iniciador para reabrir.

O código fica na pasta extraída; os bancos Docker usam volumes persistentes gerenciados pelo Docker. Configuração privada, certificados e cópias locais ficam em `.local` e `.env`. Copiar somente a pasta de código para outro computador não transporta automaticamente os volumes.

Não apague `.local` ou os volumes para corrigir um erro de abertura. Uma reinicialização integral é uma operação destrutiva separada.

### Usar outra porta

Se a porta 8080 estiver ocupada, abra o arquivo `.env` na raiz e altere apenas esta linha:

```dotenv
WEB_PORT=8081
```

Salve e execute o iniciador novamente; abra então `http://localhost:8081`. O valor é preservado nas próximas preparações. O bootstrap pode ter criado `.env` mesmo quando uma primeira inicialização falhou depois. Se o arquivo ainda não existir, conclua a preparação do Docker e tente iniciar antes de editá-lo. Não publique `.env`, pois ele também contém segredos.

### Backup e restauração

Os parâmetros `-Database` no Windows e `--database` no Mac aceitam `sql`, `nosql` ou `both`.

Neste laboratório, `backup` e `restore` executam uma volta completa de dump e restauração, com verificação de dados e medição de tempo. A restauração usa **uma base nova e separada**, com prefixo `restore_pg_` ou `restore_mongo_`; não sobrescreve a origem nem recupera a aplicação por cima dos dados atuais. Cada execução mantém um destino para inspeção e consome espaço.

As cópias mantidas ficam cifradas em `.local/backups`; a chave está em `.local/admin/backup.key`. Preserve a chave separadamente para não perder o acesso às cópias. Pause escritas durante o dump do MongoDB standalone. Os limites estão nos [riscos residuais](docs/riscos_residuais.md).

## Se algo não funcionar

| Problema | Próximo passo |
|---|---|
| Docker não encontrado ou motor indisponível | Abra o Docker Desktop, conclua suas telas iniciais e aguarde. Em um terminal novo, `docker info` deve alcançar o motor. |
| Windows com contêineres Windows ativos | Selecione contêineres Linux no Docker Desktop. Siga as orientações dele para WSL 2, se necessário. |
| Falha durante download ou build | Confira conexão e espaço livre; execute o iniciador novamente. Não apague a configuração ou os dados. |
| Endereço não abre | Aguarde o fim da inicialização, confira a porta em `.env` e execute `diagnose`. |
| Senha inválida | Use o `ACESSO_LOCAL.txt` desta instalação. Senhas de outra cópia do projeto não servem como referência. |
| Porta 8080 ocupada | Altere `WEB_PORT` como explicado acima e inicie novamente. |
| Conflito da rede 172.29.74.0/24 | O ajuste deve abranger Compose e `pg_hba.conf` juntos e ser seguido dos testes; consulte a arquitetura antes de alterar. |

Comece pelo comando `diagnose` do seu sistema e pelo estado dos serviços no Docker Desktop. Para uma listagem curta no terminal:

```sh
docker compose -p securedb-lab ps
```

Se precisar de logs, abra **Containers → securedb-lab → serviço → Logs** no Docker Desktop ou, na pasta do projeto:

```sh
docker compose -p securedb-lab logs --tail 60 api web seed
```

Examine os logs localmente. Ao pedir ajuda, informe sistema, etapa e mensagem de erro sanitizada. Não envie `.env`, `.local`, credenciais, tokens, chaves, dumps ou saídas completas de configuração resolvida.

## Validação e limites conhecidos

A revisão anterior de portabilidade observou **46 PASS e 1 SKIP na suíte nativa Windows**, **19 PASS no recorte unitário final** e **5 PASS de interface**, além de TypeScript e build aprovados. As contagens Python se sobrepõem e não devem ser somadas; o SKIP corresponde ao smoke Docker. Veja [REVISAO_DOCKER_MACOS.md](docs/REVISAO_DOCKER_MACOS.md) e o [histórico de validação](docs/VALIDACAO.md).

O motor Docker local estava indisponível nessa revisão. Esses resultados não comprovam execução dos contêineres. A CI foi preparada para Linux `amd64` e `arm64`; consulte os resultados observados em [Actions](https://github.com/KaiFlame/securedb-lab/actions). Um workflow presente no código não equivale a um job aprovado. Mac real ainda exige teste no próprio equipamento, mesmo com CI Linux ARM aprovada.

O histórico Windows comprova 17/20 controles no seu perfil; SQL-01, NOSQL-01 e NOSQL-05 dependem de ENV-01 e da implantação Docker efetiva. Uma nova instalação precisa gerar suas próprias evidências. O painel lê `evidencias/latest.json`; os arquivos sanitizados em `evidencias/entrega/` preservam execuções anteriores sem aprovar automaticamente o novo ambiente.

A aplicação demonstra segurança em ambiente local, com HTTP do navegador restrito ao computador, TLS verificado nos bancos, autorização, RLS, RBAC, validação e backups testáveis. Não constitui uma implantação de produção. Consulte a [arquitetura](docs/arquitetura.md) e os [riscos residuais](docs/riscos_residuais.md).

## Entrega acadêmica e desenvolvimento

A [matriz de rastreabilidade](docs/rastreabilidade.md), o [inventário](docs/inventario_controles.md), as [dez questões](docs/questoes_dissertativas.md), o [roteiro dos quatro simuladores](docs/simuladores.md) e o [relatório PDF](docs/relatorio_final.pdf) compõem a documentação. Continuam como tarefas do aluno: preencher integrantes/RA, revisar individualmente as respostas e coletar os simuladores com justificativas e evidências. Elas não impedem instalar ou abrir o aplicativo.

O pacote público exclui materiais FACAMP originais, dados e segredos locais. A autoria dos materiais permanece preservada; nenhuma licença de terceiros é presumida. O procedimento de revisão para publicação está em [github.md](docs/github.md), com o estado de preparação em [PRONTIDAO_GITHUB.md](docs/PRONTIDAO_GITHUB.md).

O atalho Windows nativo existente em uma máquina já preparada é um perfil separado, documentado em [uso_desktop.md](docs/uso_desktop.md); ele não é instalado ao baixar o ZIP. Desenvolvedores podem usar os scripts Python e recompilar a interface com Node/npm. Essas ferramentas continuam opcionais para quem usa o fluxo Docker descrito aqui.
