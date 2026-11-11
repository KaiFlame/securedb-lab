# Revisão de distribuição Docker e macOS — 11/11/2026

O código está preparado para revisão e primeiro commit. A instalação Docker ainda exige validação dinâmica: o Docker Engine desta máquina não está disponível. Não houve publicação, commit ou execução remota de CI.

## Alterações implementadas

- `iniciar.command`, `parar.command` e `testar.command`; CLI POSIX `scripts/docker.sh`.
- Bootstrap em contêiner, sem Python/Node/Git no host para iniciar o ZIP. Docker Desktop precisa ser instalado e configurado uma vez pelo usuário.
- Configuração idempotente: segredos, certificados, chave de backup e porta preservados. UID/GID reais do usuário no Mac/Linux; permissões de leitura específicas para a API, sem montar credenciais administrativas nela.
- Seed automático antes da API, aguardando bancos saudáveis; healthcheck também na interface web.
- Contextos Docker excluem `.venv`, `node_modules`, dados e segredos do host.
- Ferramentas MongoDB 100.13.0 por arquitetura, com SHA-256 oficial. A disponibilidade ARM64/AMD64 das cinco imagens foi conferida por metadados oficiais em `docs/compatibilidade_plataformas.json`; isso não comprova execução.
- Smoke HTTP real por Nginx/Uvicorn e CI Linux amd64/arm64 com instalação limpa, porta 18080, reinicialização/persistência, TLS, controles e backup/restore.
- Geração futura do relatório distingue perfil Docker de histórico Windows. Dois testes usam entradas sintéticas em diretórios temporários para impedir afirmações incorretas; não são evidências ENV-01.

## Verificações observadas

| Verificação | Resultado | Alcance |
|---|---|---|
| Suíte nativa com bancos e HTTP reais | 46 PASS, 0 FAIL, 1 SKIP | Windows; o SKIP é o novo smoke Docker. |
| Recorte unitário final | 19 PASS, 0 FAIL; 30 testes de integração não selecionados | Inclui dois testes do gerador adicionados após a suíte nativa; há sobreposição, não somar as contagens. |
| Interface | 5 PASS; TypeScript e Vite PASS | Respostas controladas nos testes de UI. |
| Compose principal e bootstrap | Configuração estática PASS | Não inicia serviços. Repasse de WEB_PORT=18081 ao bootstrap conferido. |
| Scripts POSIX | Sintaxe PASS nos quatro iniciadores | Shell disponível no Windows, não shell nativo do Mac. |
| Inicializador com motor ausente | Falha explícita com orientação | Não produz ENV-01 nem sucesso fictício. |
| Segredos candidatos ao Git | PASS, sem achados | Scanner do checkout; não equivale a auditoria de todas as dependências/histórico. |

Os JSON desta revisão estão em `evidencias/entrega/docker_macos_2026-11-11/`. O histórico anterior de 39 testes Python e 5 de interface, o PDF acadêmico e as capturas foram preservados. O aviso de depreciação TestClient/httpx não causou falha. Os serviços nativos abertos nesta revisão foram encerrados, preservando dados.

## O que falta

1. Criar o repositório remoto, revisar os arquivos, fazer o primeiro commit e push com a identidade do titular. A árvore foi preparada; nenhum nome/e-mail foi inventado.
2. Observar aprovação dos jobs Docker amd64 e arm64 no GitHub. Os workflows já existem, mas não executaram remotamente nesta revisão.
3. Testar no Mac real: instalar/configurar Docker Desktop, extrair/clonar, iniciar, entrar, executar `test`, parar e reabrir preservando dados. Não há garantia antecipada de funcionamento nesse equipamento.
4. Para concluir a entrega acadêmica: integrantes/RA, revisão individual das dez respostas e coleta justificada dos quatro simuladores. Os documentos e a matriz de vinte controles estão presentes. No perfil Windows, 17/20 controles seguem comprovados; SQL-01, NOSQL-01 e NOSQL-05 aguardam ENV-01 real em Docker. As pendências humanas não impedem abrir o aplicativo.

O manual e a apresentação definem requisitos acadêmicos; o prompt complementa a arquitetura e o produto. Ferramentas citadas como sugestões nos materiais não foram convertidas em novas obrigações. Os três originais permanecem em `.local/referencias`, fora do pacote público.

## Uso pelo amigo

Instale o [Docker Desktop oficial para Mac](https://docs.docker.com/desktop/setup/install/mac-install/), na versão do chip, e conclua sua primeira abertura. Depois extraia tudo e abra `iniciar.command`. Alternativa pelo Terminal, dentro do projeto:

```sh
sh scripts/docker.sh up
sh scripts/docker.sh credentials
sh scripts/docker.sh test
sh scripts/docker.sh down
```

O primeiro `up` baixa e constrói as dependências. A interface usa `http://localhost:8080`; as senhas são locais e diferentes em cada instalação. Não compartilhar `.env`, `.local`, chaves ou volumes do Windows. O guia detalhado está em `docs/instalacao_macos.md`.

Pasta canônica: `C:\Users\Guilherme\Documents\SecureDB-Lab`. O pacote público contém fontes; imagens e dependências são obtidas no primeiro build. O atalho Windows já instalado permanece apontando para essa pasta.
