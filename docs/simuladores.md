# Roteiro dos quatro simuladores de governança

Use os simuladores existentes no HTML original. Os valores são **informados pelo aluno**, mesmo quando derivados de medições. Não constituem teste automatizado nem auditoria formal. Nenhum cenário inicial foi coletado nesta execução; a comparação antes/depois permanece pendente de coleta humana, sem reconstrução fictícia do passado.

## 1. Governança de SI

Registre os dez domínios, nota 0-5, peso, justificativa e caminho de evidência: IAM 12; MFA/PAM 10; criptografia 11; rede 10; hardening 9; logging 10; BCM 12; DevSecOps 9; privacidade 8; risco/compliance 9. O índice didático é a soma ponderada das notas dividida por 5 (pesos somam 100). Registre nível e quatro lacunas destacadas. Não conceda nota máxima por haver um arquivo de configuração.

## 2. IAM e exposição

Anote ambiente, banco, privilégio, autenticação administrativa, endpoint público, segredo versionado, recertificação, logs, identidade de workload e break-glass. Compare somente alterações comprovadas e cite controles SQL-02/03/04 e NOSQL-02/03/04/05. Uma senha estática de serviço não é identidade de workload federada. Não marque MFA/PAM ou recertificação sem processo real.

## 3. BCM / RTO / RPO

Defina requisitos do cenário fictício com justificativa do aluno, sem apresentá-los como requisito do professor. Copie `backup_seconds` e `restore_seconds` dos testes SQL-09/NOSQL-09, considerando que o tempo de recuperação do serviço completo inclui mais que o restore do banco. Frequência de backup não foi automatizada; logo, não há RPO operacional garantido. HA, offsite, imutabilidade e plano de DR completo permanecem ausentes. Cópia AES-GCM no mesmo host não atende sozinha 3-2-1-1-0.

## 4. Plano de evolução

Registre nível atual/alvo, gap, prioridade e ambiente. Propostas P1: (a) backups agendados/offsite/imutáveis e chave em cofre; (b) identidade administrativa com MFA/PAM e revisão de acesso; (c) centralização de logs, retenção e alertas. Responsáveis: preencher pelo grupo. Evidências esperadas: execução e logs de restore, revisão assinada de acesso e alerta observado. São propostas, não controles existentes.

## Coleta

Salve em `evidencias/simuladores/` os quatro pares de capturas quando houver cenário inicial verdadeiro, justificativas em Markdown e um JSON com `origem: informado pelo aluno`, data, parâmetros, resultado, evidência e limitações. Se não houver captura inicial, registre “não coletado”; não simule uma captura retroativa. Revise limitações da fórmula do HTML antes de interpretar mudanças de pontuação como ganho real de segurança.
