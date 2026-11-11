# Preparação para GitHub

O diretório já contém Git local na branch main, `.gitignore`, `.dockerignore`, lockfile npm, workflows e templates. Não há remote configurado e nada é publicado automaticamente.

O ZIP de distribuição contém os arquivos publicáveis e exclui `.git`, `.local`, dependências e segredos. Se estiver usando uma extração do ZIP, execute primeiro `git init --initial-branch=main` nessa pasta.

1. Execute `python scripts/lab.py preflight` e revise o que será versionado.
2. Execute `git status --short` e `git diff --cached`. `.local`, `.env`, dados, dumps e chaves devem permanecer ignorados.
3. Identificação: preencha integrantes e RA no relatório. Escolha conscientemente a licença do código original. Os materiais FACAMP têm autoria própria e não são relicenciados por este projeto.
4. Configure seu nome/e-mail do Git caso necessário; não use identidade inventada.
5. Crie o repositório vazio no GitHub e use a URL que ele fornecer:

```sh
git add .
git add --chmod=+x iniciar.command parar.command testar.command scripts/*.sh
git commit -m "Implementa laboratórios SecureDB FACAMP"
git remote add origin <URL-DO-REPOSITORIO-CRIADO>
git push -u origin main
```

Não cole senhas em issues, PRs, terminal compartilhado ou README. Antes do primeiro push, confira também o histórico caso tenha feito commits anteriores. O preflight verifica os arquivos rastreados e candidatos não ignorados do checkout; não é prova de ausência de qualquer segredo no histórico ou em serviços externos.

A matriz de integração foi configurada para Linux amd64 e arm64: início sem Python/Node do host, HTTP publicado, persistência após down/up e testes com Nginx, TLS e backup/restore. Cada job precisa ser observado no GitHub. CI Linux ARM não substitui teste no Mac real.

A CI unitária usa dados sintéticos e gera sua própria configuração local. A CI de integração sobe o Compose e executa bancos reais, produzindo um artefato de evidências sanitizadas. O sucesso da CI só pode ser declarado depois que a execução ocorrer no repositório do aluno. Nenhum badge de aprovação remota foi incluído.
