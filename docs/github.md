# Repositório GitHub e manutenção

Repositório público: **https://github.com/KaiFlame/securedb-lab**. O projeto desta pasta usa esse endereço como `origin`, na branch `main`. O primeiro commit publicado foi `fd465892b50a19a007ada79ea2ab407edd5cb3e7`.

Para instalar em outro computador, siga o [README Windows/macOS](../README.md). Baixar por ZIP dispensa Git, Python e Node no host; Docker Desktop precisa estar instalado e configurado. Os dados e segredos desta máquina não acompanham o repositório.

## Validação da publicação

O clone público sem autenticação e o download real por **Code → Download ZIP** foram conferidos. O arquivo contém os iniciadores dos dois sistemas, conserva a permissão executável dos `.command` e exclui `.env`, `.local`, `.venv`, dependências e dados privados.

Os workflows foram disparados, mas os jobs de testes não iniciaram por indisponibilidade de execução na conta GitHub. Logo, ainda não há aprovação remota da instalação Docker. Veja os resultados oficiais de [integração Docker](https://github.com/KaiFlame/securedb-lab/actions/runs/43090005494) e [unitários/interface/Windows](https://github.com/KaiFlame/securedb-lab/actions/runs/43090005597). Um check sem execução não é falha demonstrada do código nem teste aprovado. Mac real e Docker Desktop Windows precisam de execução observada.

## Novas alterações pelo mantenedor

Revise os arquivos e execute os testes adequados antes de publicar. Na instalação Windows preparada:

```powershell
.venv\Scripts\python scripts/preflight.py
git status --short
git diff
git add .
git diff --cached --check
git commit -m "Descreve a alteração"
git push
```

`preflight.py` verifica arquivos rastreados e candidatos não ignorados; não certifica todo o histórico ou todas as dependências. Não envie `.env`, `.local`, credenciais, tokens, chaves, dumps ou logs brutos. Não use push forçado para resolver divergências sem revisar a origem delas.

Os materiais FACAMP originais permanecem fora do repositório. Os relatórios e as evidências históricas preservam o perfil em que foram produzidos. A licença do código original ainda deve ser escolhida por seu titular; nenhuma licença de terceiros foi presumida.
