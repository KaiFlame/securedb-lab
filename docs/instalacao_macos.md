# Instalação no macOS

O fluxo portátil usa Docker e Compose. O Mac não precisa ter Python, Node ou Git para executar o ZIP. O aplicativo ainda não foi testado em um Mac real; as verificações anteriores foram feitas no Windows nativo.

## Preparação única do Docker

Em **Sobre Este Mac**, identifique se o computador usa chip Apple ou processador Intel. Instale o Docker Desktop correspondente, mova-o para Aplicativos, abra-o e conclua as telas iniciais. A aceitação dos termos deve ser feita pelo usuário; sem ela o motor não inicia. Siga a [instalação oficial do Docker para Mac](https://docs.docker.com/desktop/setup/install/mac-install/).

Aguarde o Docker indicar que está em execução. A instalação do Docker é um pré-requisito externo: os arquivos do laboratório não o instalam nem aceitam seus termos automaticamente.

## Extrair e iniciar

Extraia todo o ZIP para uma pasta local. Como exemplo, use `Documents/SecureDB-Lab`; mantenha juntos `docker-compose.yml`, `scripts`, `api`, `web` e os demais diretórios.

Abra `iniciar.command`. Ele chama `sh scripts/docker.sh up` a partir da pasta do projeto. Na primeira execução, o download das imagens e o build podem demorar. O bootstrap prepara segredos e certificados, e o serviço de seed cria as contas de demonstração; a inicialização aguarda os serviços.

Se o Finder não executar o arquivo, use o Terminal:

```sh
cd "$HOME/Documents/SecureDB-Lab"
sh scripts/docker.sh up
```

Ajuste o caminho caso tenha extraído em outro lugar. Para permitir o duplo clique após a extração:

```sh
chmod +x iniciar.command parar.command testar.command
```

Abra [http://localhost:8080](http://localhost:8080). Para mostrar os acessos sintéticos apenas no seu terminal:

```sh
sh scripts/docker.sh credentials
```

Não publique essa saída. A Empresa A usa `aurora.editor`, a B usa `vertice.editor`; `aurora.leitor` tem acesso de leitura na A.

## Testar, parar e reabrir

`testar.command` executa a suíte; `parar.command` encerra os serviços preservando os volumes. Fechar a aba do navegador não encerra o laboratório. Reabra com `iniciar.command`.

Pelo Terminal, os comandos equivalentes são:

```sh
sh scripts/docker.sh test
sh scripts/docker.sh diagnose
sh scripts/docker.sh down
```

Os testes usam bancos reais, acrescentam dados sintéticos e produzem evidências. O painel só aprova um controle quando seus testes exigidos passam; itens não executados continuam pendentes.

## Porta e recuperação

Depois da primeira preparação, edite `WEB_PORT` no arquivo `.env` para usar outra porta local, por exemplo `8081`. Não altere as senhas geradas. Execute `up` novamente e abra `http://localhost:8081`. A configuração da porta é preservada nas próximas execuções.

Para exercícios de recuperação e geração do relatório:

```sh
sh scripts/docker.sh backup --database both
sh scripts/docker.sh restore --database both
sh scripts/docker.sh report
```

`--database` também aceita `sql` e `nosql`. As rotinas fazem dump/restauração em destinos novos, verificam os dados e medem o tempo; não sobrescrevem a base de origem. Pause escritas durante o dump MongoDB standalone. Consulte os detalhes e a guarda da chave no [README](../README.md).

## Quando não inicia

| Sintoma | Verificação |
|---|---|
| Docker não encontrado ou motor indisponível | Confirme a instalação, abra o Docker Desktop e conclua suas telas iniciais. No Terminal, `docker info` deve alcançar o motor. |
| Falha de download ou build | Confira a conexão com a Internet e o espaço disponível. Execute novamente `sh scripts/docker.sh up`; preserve `.env` e `.local`. |
| Porta 8080 ocupada | Altere `WEB_PORT` em `.env` e execute `up` novamente. |
| Interface indisponível | Aguarde o término do comando e execute `sh scripts/docker.sh diagnose`. Confira também os serviços no Docker Desktop. |
| Conflito da subnet 172.29.74.0/24 | O ajuste deve abranger Compose e `pg_hba.conf` conjuntamente; depois é necessário reexecutar os testes de rede e autenticação. |

Não remova volumes ou `.local` para tentar corrigir uma falha de inicialização. `down` preserva os dados; remoção integral é um procedimento separado e destrutivo.

## Alcance da validação

A execução Docker está pendente neste computador porque seu motor não ficou disponível. A CI foi preparada para Linux `amd64` e `arm64`; uma aprovação em Linux ARM será evidência dessa plataforma, não de teste em macOS. A validação final do Mac deve observar instalação, início, login, testes, parada e reabertura no próprio equipamento. Veja [PRONTIDAO_GITHUB.md](PRONTIDAO_GITHUB.md).

Integrantes/RA, revisão das respostas e coleta dos simuladores são pendências acadêmicas separadas. Os materiais FACAMP originais devem ser obtidos pelos canais da disciplina e não acompanham o pacote público.
