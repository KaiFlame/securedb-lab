# Simuladores de governança

Fonte: apresentação FACAMP, slides 67–70, e Manual do Aluno, pp. 5–8. Os simuladores foram executados no HTML original em 11/11/2026. A versão acadêmica inclui as capturas. O cenário inicial dos simuladores 1 a 3 ficou **não coletado**. Os resultados abaixo registram o cenário atual e, no simulador 3, uma hipótese de planejamento. Os valores e as recomendações calculadas estão em `evidencias/simuladores/resultados-macos.json`.

## 1. Governança de SI — 31/100, nível 2 (Repetível)

| Domínio | Nota / 5 | Justificativa |
|---|---|---|
| IAM | 2 | Papéis segregados e operações permitidas e negadas verificadas nos dois bancos. |
| MFA/PAM | 0 | Administração por senha, sem MFA/PAM demonstrados. |
| Criptografia | 2 | TLS verificado nos bancos e restauração a partir de backups cifrados. |
| Rede | 2 | ENV-01 observou a rede interna do Compose e os bancos sem portas publicadas. |
| Hardening | 1 | Configurações de segurança registradas. Falta rotina de revisão e atualização. |
| Logging/SIEM | 2 | Eventos de conexão e DDL observados no PostgreSQL e trilha da aplicação. Falta centralização e alerta. |
| BCM/DR | 2 | Restaurações verificadas em bases separadas. Backups sob demanda no mesmo host. |
| DevSecOps | 1 | Testes locais repetíveis. Evidência limitada de automação contínua. |
| Privacidade/LGPD | 2 | Dados sintéticos e separação por empresa. Governança de retenção e conformidade ainda por definir. |
| Risco/compliance | 1 | Riscos residuais documentados. Falta rotina de revisão e definição de responsáveis. |

O HTML destacou MFA/PAM, hardening, DevSecOps e gestão de riscos.

## 2. IAM e exposição — 60/100, postura Controlada

Ambiente local (on-premises), SQL + NoSQL, mínimo privilégio e segregação, senha administrativa forte, endpoint público desmarcado e auditoria marcada pelos logs locais. O item de senha em código/.env real foi marcado porque a instalação gera um .env local com credenciais. O arquivo é ignorado pelo Git. Recertificação, identidade federada de workload e acesso de emergência controlado ficaram desmarcados. Evidências: ENV-01, SQL-02/03/04/08 e NOSQL-02/03/04/05.

## 3. BCM — cenário hipotético, 36/100, Insuficiente

As restaurações foram medidas com dados pequenos. PostgreSQL: dump de 0,1082 s, restauração e verificação de 0,1472 s. MongoDB: dump de 0,0298 s, restauração e verificação de 0,1116 s. Os destinos separados foram verificados nos testes SQL-09 e NOSQL-09. Esses tempos medem a recuperação dos bancos com os dados do teste.

O simulador exige uma frequência. Como os backups reais são manuais, o campo foi preenchido com uma **hipótese** diária para mostrar a lacuna em relação a um RPO proposto de 8 horas. O exercício usa RTO proposto de 1 hora e estimativa de 30 minutos para recuperar o serviço, incluindo atividades além do restore. Os valores representam um cenário didático para discussão. A única opção marcada foi backup criptografado. A restauração observada foi pontual e a opção de teste periódico ficou desmarcada. Na operação atual, a frequência manual deixa o RPO sem garantia.

## 4. Plano de evolução — nível 2 para 3

O HTML calculou lacuna de 1 nível e esforço baixo para o foco de redução de risco em ambiente local. A tabela transforma as recomendações do simulador em ações do grupo, com responsáveis propostos por função. A revisão periódica fica em P3 como etapa de acompanhamento definida para a entrega.

| Prioridade | Ação proposta | Responsável proposto | Evidência esperada |
|---|---|---|---|
| P1 | Revisar acesso administrativo, avaliar MFA/PAM e atualizar o registro de riscos. | Segurança e infraestrutura | Matriz de acesso revisada e registro de riscos com responsáveis. |
| P2 | Definir periodicidade e retenção de backups, separar a cópia e testar a restauração. | Administração dos bancos | Agenda, registro de restauração e comparação dos dados. |
| P2 | Centralizar logs e formalizar a revisão de privilégios e de atualizações. | Operação e segurança | Evento recebido no destino e registro da revisão. |
| P3 | Revisar as ações após novo exercício e atualizar a pontuação com as evidências obtidas. | Grupo | Comparação datada e inventário de controles atualizado. |
