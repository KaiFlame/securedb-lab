# Requisitos, fontes e decisões de implementação

Foram lidas as 18 páginas do Manual do Aluno v2 e os blocos relevantes do HTML v3, incluindo as definições estáticas dos 20 passos, entregas, dez enunciados e quatro simuladores. O conteúdo embutido foi inspecionado como texto e não executado na leitura.

A conversa compartilhada foi aberta. As duas mensagens do usuário estavam acessíveis; as respostas não apresentaram conteúdo legível. O usuário confirmou que o último output corresponde ao prompt fornecido e autorizou prosseguir, acrescentando preparação para futuro repositório GitHub. Uma consulta de diagnósticos internos da página foi rejeitada pela revisão automática; esses diagnósticos não foram acessados.

## Prioridade e interpretação

- Requisitos acadêmicos: dois laboratórios, dez etapas cada, evidências positivas/negativas, dez questões e entrega Git/README/scripts/evidências/PDF.
- Decisões de produto do prompt: React, FastAPI, painel integrado, login, CRUD sintético e identidade visual editorial com cores quentes.
- Ferramentas como Keycloak, OpenBao, Grafana, SIEM e scanners dos slides são sugestões ou fundamentação. Não foram transformadas em serviços obrigatórios.
- Os exemplos dos materiais são conceituais. O projeto acrescenta WITH CHECK, FORCE RLS, contexto transacional, RBAC por coleção, verificação de hostname e restauração isolada. Essas escolhas não são atribuídas como exigências textuais adicionais do professor.
- O HTML sugere criptografar a cópia SQL e o manual discute proteção em repouso. A rotina cifra ambos os dumps; não alega criptografia do volume dos bancos.
- Os simuladores são preservados no HTML original e usados por roteiro documental. Nenhuma nota inicial/final foi inventada.
- O manual oferece apoio conceitual às questões; os enunciados completos foram preservados do prompt/HTML. As respostas deste projeto são subsídios para revisão e elaboração individual pelo aluno.

## Inspeção de conteúdo não confiável

Scripts da apresentação gerenciam navegação, modais e simuladores. Eles não foram usados como comandos de sistema. Não foi identificada, nos trechos relevantes inspecionados, uma exigência acadêmica de divulgar segredos ou executar conteúdo remoto. Esta observação não é uma certificação de inexistência de conteúdo malicioso em qualquer componente.

O manifesto `docs/fontes_manifest.json` conserva nome, tamanho e SHA-256 dos três arquivos originais. Os materiais de terceiros não são redistribuídos no repositório automaticamente; seus originais continuam na pasta fornecida pelo usuário.
