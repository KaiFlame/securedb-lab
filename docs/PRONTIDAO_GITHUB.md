# Prontidão para GitHub

> Publicação confirmada posteriormente: [PUBLICACAO.md](PUBLICACAO.md). O repositório e o commit existem; a CI disparou, mas seus jobs não iniciaram. Os estados de preparação abaixo são históricos.

> Preparação posterior: README Windows/macOS e iniciador PowerShell 5.1 conferidos; 30 verificações do iniciador (Docker simulado) e 19 testes unitários Python aprovados. Veja [PREPARACAO_PUBLICACAO.md](PREPARACAO_PUBLICACAO.md). O estado histórico abaixo não equivale ao estado remoto atual.

O projeto está preparado para revisão e futura publicação do código. Nesta preparação não foram criados commits, configurados remotes ou enviados arquivos ao GitHub. A presença de workflows não comprova que a CI tenha executado.

## Instalação e validação técnica

| Item | Estado documentado | Próxima verificação |
|---|---|---|
| Aplicação Windows nativa | 46 PASS e 1 SKIP Docker na suíte nativa; 19 PASS no recorte unitário final; 5 de interface. Contagens Python se sobrepõem | Consultar o perfil e as evidências em `VALIDACAO.md`. |
| Fluxo Docker portátil | Implementado; execução dinâmica ainda pendente | Executar início, readiness, suíte, diagnose, backup/restore e encerramento com motor disponível. |
| Linux amd64 e arm64 | Matriz de CI preparada, sem resultado remoto observado | Conferir cada job e seus artefatos após o primeiro envio autorizado. |
| macOS Intel e Apple Silicon | Orientações e iniciadores preparados; Mac real não testado | Testar no equipamento de destino; CI Linux não substitui essa verificação. |
| Segredos, TLS e contas | Gerados localmente pelo bootstrap e seed | Conferir idempotência e preservação de `WEB_PORT` no fluxo Docker. |
| Vinte controles | 17 comprovados no perfil nativo e 3 de implantação pendentes | Observar ENV-01 e suíte integrada no perfil Docker antes de aprovar SQL-01, NOSQL-01 e NOSQL-05. |

Para o usuário do ZIP, os bloqueios de instalação são Docker Desktop ausente/não iniciado, termos ainda não aceitos, falha de download/build, conflito de porta ou recursos insuficientes. Python, Node e Git não são pré-requisitos desse fluxo.

## Conteúdo publicável

O repositório deve conter código, configurações sem segredos, scripts, testes, documentação, relatório e evidências sanitizadas. O ZIP público também inclui os iniciadores `iniciar.command`, `parar.command` e `testar.command`.

Devem permanecer fora da publicação:

- `.env`, `.local`, `.venv`, dependências instaladas e dados dos bancos;
- senhas, tokens, chaves privadas, logs brutos e dumps, inclusive cópias cifradas locais;
- os materiais FACAMP originais e as cópias privadas em `.local/referencias`.

O manifesto de fontes identifica os materiais consultados. Sua inclusão como referência não concede direito de redistribuição. A licença do código original precisa ser escolhida por quem tem esse direito; nenhuma licença foi presumida para código ou materiais de terceiros.

Antes do primeiro envio, revise os arquivos candidatos, execute o preflight de segredos e confira também o histórico se houver commits anteriores. O scanner do checkout não é garantia sobre todo o histórico ou serviços externos. O procedimento está em [github.md](github.md).

## Pendências acadêmicas

Estas tarefas não impedem instalar ou abrir a aplicação:

- preencher integrantes e RA no relatório, sem inventar identificação;
- revisar individualmente as dez respostas, conectando conceito, risco, configuração, evidência e limitação;
- coletar os quatro simuladores com parâmetros justificados e evidências de controles realmente comprovados;
- registrar “não coletado” quando não houver cenário inicial verdadeiro, sem reconstruir capturas ou pontuações retrospectivas.

A entrega mínima do manual reúne Git, README, scripts, evidências e relatório PDF. A [matriz de rastreabilidade](rastreabilidade.md) distingue requisito implementado, teste executado e pendência humana. Essas pendências devem continuar visíveis no relatório final.

## Após o envio autorizado

Acompanhe os jobs Linux `amd64` e `arm64`, confira falhas e artefatos sanitizados e atualize o estado somente com resultados observados. Depois, faça o smoke no Mac real: iniciar, consultar credenciais, entrar, executar testes, parar e reabrir preservando os dados. Não acrescente badge de aprovação antes de uma execução remota bem-sucedida.

Registro atual: [REVISAO_DOCKER_MACOS.md](REVISAO_DOCKER_MACOS.md).
