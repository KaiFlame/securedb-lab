# Preparação para publicação — 11/11/2026

O usuário autorizou criar um repositório público em `KaiFlame/securedb-lab`. O README foi refeito para quem baixa por ZIP ou clona, com caminhos equivalentes Windows/macOS e guias próprios. A criação remota aguarda autenticação na conta do titular; não foi declarada publicação bem-sucedida sem confirmação do GitHub.

Foram acrescentados os iniciadores `iniciar.cmd`, `parar.cmd`, `testar.cmd` e `scripts/docker.ps1`, compatíveis com Windows PowerShell 5.1. Docker Desktop é o pré-requisito externo; Python, Node, Git e Git Bash não são exigidos para usar o ZIP. O Docker baixa e constrói as dependências da aplicação.

Validações desta preparação: 30 verificações do iniciador Windows aprovadas no PowerShell 5.1 (parser, codificação, falhas e fluxos com Docker simulado); 19 testes unitários Python aprovados. Essas verificações não comprovam execução de contêineres. O histórico nativo permanece com 46 PASS e 1 SKIP Docker, além de 5 testes de interface e build aprovados. As contagens Python se sobrepõem.

O Docker Engine local continua indisponível. A CI preparada inclui Linux amd64 e arm64 com bancos reais e um job Windows que verifica o iniciador com chamadas controladas; nenhum resultado remoto foi presumido. Macs Intel/Apple Silicon e Docker Desktop Windows ainda exigem validação nos respectivos equipamentos.

O preflight verifica todos os candidatos Git sem expor senhas. Uma revisão independente também inspecionou padrões de segredos, PDFs e seis capturas; não identificou credenciais publicáveis. O link para a conversa de contexto foi removido da documentação pública atual. Caminhos da instalação Windows aparecem em registros históricos; não são dependências de execução. Os materiais originais FACAMP, dados, chaves e credenciais continuam fora do Git.

O estado remoto efetivo deve ser conferido em `https://github.com/KaiFlame/securedb-lab` e em Actions. Os documentos históricos preservam as condições em que cada resultado foi produzido. Pendências acadêmicas: integrantes/RA, revisão individual das dez respostas e coleta justificada dos quatro simuladores.
