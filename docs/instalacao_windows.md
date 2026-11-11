# Instalação no Windows

Este guia usa Docker Desktop e os iniciadores `.cmd` do projeto. Para executar o ZIP, não é necessário instalar Python, Node, Git ou Git Bash.

## 1. Preparar o Docker

Instale o [Docker Desktop oficial para Windows](https://docs.docker.com/desktop/setup/install/windows-install/), siga a preparação de WSL 2 indicada por ele e use contêineres Linux. Reinicie o computador se o instalador solicitar. Abra o Docker Desktop pelo menu Iniciar, conclua a primeira configuração e aceite os termos se concordar. Aguarde o motor ficar em execução.

O projeto não instala o Docker, habilita recursos do Windows ou aceita termos automaticamente. Siga as orientações oficiais se WSL 2 ou virtualização precisarem de configuração.

## 2. Baixar e extrair

1. Abra [KaiFlame/securedb-lab](https://github.com/KaiFlame/securedb-lab).
2. Clique em **Code → Download ZIP**.
3. No arquivo baixado, escolha **Extrair tudo**.
4. Entre na pasta extraída que contém `README.md` e `docker-compose.yml`.

Ative a opção **Extensões de nomes de arquivo** no Explorador se precisar distinguir `iniciar.cmd` de `iniciar.command`. O `.cmd` é o iniciador Windows; o `.command` é destinado ao Mac. Execute a partir da pasta extraída, mantendo os demais arquivos juntos.

Se preferir Git, e já o tiver instalado:

```powershell
git clone https://github.com/KaiFlame/securedb-lab.git
cd securedb-lab
```

Clonar ou baixar copia o código. Não traz os bancos atuais ou as credenciais privadas de outra máquina.

## 3. Iniciar

Com o Docker Desktop aberto, dê duplo clique em **iniciar.cmd**. Acompanhe a janela até terminar a preparação. A primeira execução baixa imagens, constrói serviços, gera certificados e senhas e cria os usuários sintéticos. Os dados serão reaproveitados nas próximas aberturas.

Ao terminar, abra [http://localhost:8080](http://localhost:8080). Consulte a senha de cada usuário em `.local\ACESSO_LOCAL.txt`, dentro da pasta do projeto:

| Usuário | Contexto |
|---|---|
| `aurora.editor` | Empresa A, leitura e escrita |
| `vertice.editor` | Empresa B, leitura e escrita |
| `aurora.leitor` | Empresa A, somente leitura |

A empresa é definida pela identidade autenticada. Para conferir a outra empresa, encerre a sessão e entre com o usuário correspondente. Não compartilhe o arquivo de acessos ou `.env`.

## 4. Testar e parar

- **testar.cmd:** executa a suíte sobre bancos reais e gera evidências. Pode acrescentar dados sintéticos.
- **parar.cmd:** encerra os contêineres preservando os volumes e as credenciais.
- **iniciar.cmd:** reabre o ambiente com os dados preservados.

Fechar o navegador não encerra os serviços. O atalho nativo que já existe em uma máquina previamente preparada é outro perfil, descrito em [uso_desktop.md](uso_desktop.md); não é necessário para este fluxo Docker.

## Alternativa pelo PowerShell

Abra a pasta do projeto no Explorador, digite `powershell` na barra de endereço e pressione Enter. Execute os comandos abaixo nessa janela:

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

A opção `-ExecutionPolicy Bypass` se aplica somente ao processo iniciado e não altera a política permanente do Windows. `-Database` aceita `sql`, `nosql` ou `both`.

As rotinas de backup/restore medem uma volta completa de dump e restauração em base nova. Não sobrescrevem a origem e não substituem um procedimento de recuperação da aplicação em produção. Veja [preservação e recuperação no README](../README.md#backup-e-restauração).

## Resolver os primeiros problemas

**Docker não foi encontrado ou não iniciou.** Confirme a instalação, abra o Docker Desktop e conclua suas telas iniciais. Abra um novo PowerShell e verifique:

```powershell
docker info --format "{{.OSType}}"
```

O resultado esperado é `linux`. Falha de conexão indica que o motor ainda não está acessível; `windows` indica que o modo de contêiner precisa ser trocado no Docker Desktop.

**A porta 8080 está ocupada.** Depois de o bootstrap gerar `.env`, abra esse arquivo na raiz do projeto e altere somente `WEB_PORT=8080` para `WEB_PORT=8081`. Salve no próprio `.env`, sem acrescentar `.txt`, execute `iniciar.cmd` novamente e use `http://localhost:8081`. O arquivo pode existir mesmo após uma primeira tentativa que falhou mais adiante; a porta escolhida é preservada.

**A janela encerrou com erro ou a interface não abre.** Execute `up` pelo PowerShell para acompanhar a mensagem e depois `diagnose`. Para consultar o estado e os logs locais:

```powershell
docker compose -p securedb-lab ps
docker compose -p securedb-lab logs --tail 60 api web seed
```

Os serviços também aparecem no Docker Desktop em **Containers → securedb-lab**. Ao pedir ajuda, informe a etapa e o erro sanitizado. Não publique logs brutos, `.env`, `.local`, senhas, tokens ou chaves. Não remova volumes ou `.local` como tentativa de conserto: os dados dependem deles.

## Estado da validação

Os resultados nativos anteriores foram 46 PASS e 1 SKIP, mais um recorte unitário de 19 PASS com sobreposição e 5 PASS de interface. Eles não comprovam execução Docker. Consulte a [revisão registrada](REVISAO_DOCKER_MACOS.md) e os resultados realmente observados da [CI](https://github.com/KaiFlame/securedb-lab/actions).

Integrantes/RA, revisão individual das respostas e coleta dos quatro simuladores são pendências acadêmicas separadas e não impedem iniciar o aplicativo.
