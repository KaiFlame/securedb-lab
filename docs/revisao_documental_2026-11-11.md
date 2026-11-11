# Conferência complementar dos materiais FACAMP

Fontes: prompt mestre fornecido, manual v2 de 18 páginas e apresentação HTML v3. Os hashes dos três originais estão no manifesto de fontes; as cópias locais estão em `.local/referencias`.

## Correspondência com o pedido

- **Seção D, catálogo/perfis:** pesquisa e edição presentes para ambos. A busca de perfis que faltava foi implementada e testada com filtro de segmento, literalização e bloqueio de operadores/tenant.
- **Seção E, evidências:** cada controle agora tem objetivo, fonte, excerto, cenários positivo/negativo, resultados e limite residual. A UI não executa comandos administrativos. A exportação inclui o comprovante de ambiente quando esse comprovante pertence ao perfil executado.
- **Reprodutibilidade:** o inicializador do atalho usa os executáveis e a venv da instalação. Há comandos de subir, parar, testar, dump/restore, gerar PDF e limpar apenas caches. A reinicialização destrutiva está documentada separadamente e não foi executada.
- **20 etapas:** implementadas; 17 têm a comprovação nativa registrada. As três dependentes do ambiente Compose não foram promovidas artificialmente para PASS.
- **Dez questões:** enunciados mantidos literalmente, respostas em cinco partes e espaço de revisão individual. Não foi inventado nome/RA.
- **Simuladores:** roteiro dos quatro existente; resultados antes/depois não foram inventados. Continua necessária a coleta do aluno no material original.
- **Entregáveis:** código Git local, README, configurações/scripts, evidências sanitizadas, matriz, riscos e PDF presentes. O repositório remoto fica para o aluno criar.

A revisão não transforma os componentes teóricos opcionais dos slides em exigências adicionais. MFA/PAM, SIEM, HA, offsite e auditoria Enterprise permanecem limites/propostas, sem alegação de implementação.
