# Roteiro de demonstração e capturas

1. Apresente problema, dados sintéticos e diagrama. Explique diferenças entre controles implementados, comprovados e pendentes; identifique o perfil de execução real do relatório.
2. Entre como aurora.editor. Mostre os pedidos da Aurora e crie um pedido. Abra os detalhes e aprove o rascunho. Mostre a transição inválida no teste automatizado.
3. Saia e entre como vertice.editor. Mostre os dados distintos. Use SQL-06 para demonstrar SELECT/INSERT/UPDATE entre empresas bloqueados diretamente no banco e na API. Volte como aurora.leitor e mostre escrita negada.
4. Abra catálogo e perfis. Faça cadastro/edição com dados example.test. Mostre NOSQL-07: escrita inválida enviada diretamente por PyMongo recebeu código 121 do MongoDB.
5. Abra SQL-05/NOSQL-06 e apresente sessão TLS e negativas de certificado/canal inseguro. Explique por que TLS não substitui rede ou RBAC.
6. Execute `python scripts/lab.py test` na CLI com Compose funcional e atualize o painel. Mostre que não há botão de aprovação manual.
7. Apresente SQL-09/NOSQL-09: destino separado, contagens/fingerprints iguais, cópia cifrada e tempos medidos. O tempo do teste não equivale ao RTO de uma organização.
8. Explique limitações, questões dissertativas e pendências de coleta dos simuladores. Encerre com riscos residuais e controles adicionais propostos.

Capturas a produzir pelo aluno no ambiente final: contêineres ativos e rede; duas identidades/empresas; bloqueio de acesso; sessão TLS; rejeição de schema; evidência de restore; quatro simuladores antes/depois quando houver coleta inicial. Capturas produzidas nesta entrega são apenas as que constam no manifesto de validação visual; nenhuma imagem representa teste não executado.
