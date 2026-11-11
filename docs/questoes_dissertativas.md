# Dez questões dissertativas

Respostas para apresentação oral, com exemplos dos laboratórios e evidências da execução local quando disponíveis. As questões seguem os slides 76 e 77 e o Manual do Aluno, pp. 16–17.

## 1. Explique por que a aplicação não deve utilizar uma conta administrativa do PostgreSQL. Relacione sua resposta às roles criadas no laboratório e aos princípios de least privilege e segregação de funções.

A aplicação não deve usar uma conta administrativa porque essa conta tem muitos privilégios. Se a aplicação for invadida, alguém poderia alterar ou excluir dados e até modificar configurações importantes do banco. Por isso, o ideal é criar roles com permissões específicas, como uma para consultas e outra para as operações de escrita necessárias. Isso aplica o privilégio mínimo, ou seja, cada conta recebe apenas o acesso de que precisa. Também respeita a segregação de funções, separando a administração das tarefas comuns da aplicação. No laboratório, isso pode ser demonstrado mostrando as permissões das roles e uma operação administrativa negada à conta da aplicação.

## 2. Considere que o PostgreSQL foi instalado em um servidor interno. Descreva como pg_hba.conf, firewall, SCRAM e TLS trabalham juntos para reduzir o risco de acesso indevido ao banco.

Esses quatro recursos funcionam como camadas de proteção. O firewall limita quais máquinas conseguem chegar à porta do banco. O arquivo pg_hba.conf determina quais usuários, bancos e origens podem tentar uma conexão e qual método de autenticação será exigido. O SCRAM faz a verificação de senha de forma mais segura, e o TLS criptografa a comunicação para proteger os dados em trânsito. Assim, não dependemos de uma única barreira. Como evidência, podemos apresentar a regra de conexão segura, uma tentativa de acesso bloqueada e uma conexão estabelecida com TLS.

## 3. No cenário multiempresa, explique como Row-Level Security ajuda a impedir que um usuário de uma empresa consulte pedidos de outra. Indique também uma limitação do uso de RLS.

A RLS é uma segurança em nível de linha. Ela permite definir regras para que cada empresa consiga consultar apenas os pedidos que pertencem a ela, mesmo que todas utilizem a mesma tabela. Por exemplo, a empresa A não deve enxergar os registros da empresa B. Isso ajuda a evitar vazamento de informações entre clientes. Uma limitação é que superusuários podem ignorar essa proteção; além disso, regras mal configuradas ou um identificador de empresa informado incorretamente podem comprometer o isolamento. Para comprovar o controle, podemos testar a consulta de uma empresa e verificar que os pedidos da outra não aparecem.

## 4. Explique por que prepared statements são essenciais mesmo quando a aplicação já valida campos do formulário. Use um exemplo do laboratório para diferenciar validação de entrada e parametrização.

A validação verifica se o dado digitado está no formato esperado, como um e-mail válido ou um número. Já os prepared statements, usados com parâmetros, separam os dados do comando SQL. Assim, mesmo que alguém digite um texto malicioso, o banco trata esse conteúdo como valor, e não como parte da consulta. Por exemplo, em um campo de login ou de busca, a entrada do usuário deve ser enviada como parâmetro, nunca colada diretamente no SQL. Por isso, validar e parametrizar são cuidados diferentes e complementares: um confere a entrada e o outro previne que ela altere a estrutura do comando.

## 5. Proponha um conjunto mínimo de logs, alertas e evidências de backup/restore que deveriam ser mantidos para demonstrar segurança e capacidade de recuperação do banco SQL.

Para demonstrar segurança, o banco deve registrar tentativas de login, falhas de autenticação, mudanças de permissões, alterações importantes na estrutura do banco e operações críticas. Também é útil ter alertas para muitas tentativas de acesso, privilégios elevados inesperadamente e atividades fora do padrão. Para a recuperação, não basta guardar um backup: precisamos registrar quando ele foi feito, se terminou corretamente e se foi possível restaurar os dados em um teste. Isso se relaciona ao BCM, que busca manter ou recuperar a operação, e aos conceitos de RTO (tempo aceitável para recuperar o serviço) e RPO (quantidade aceitável de dados perdidos). As evidências seriam logs, alertas, registros dos backups e uma restauração testada.

## 6. Explique a diferença entre a conta administrativa e a conta da aplicação. Quais riscos surgem quando a aplicação recebe permissões além das necessárias?

No MongoDB, a conta administrativa é usada para gerenciar o banco, seus usuários e suas configurações. A conta da aplicação deve ter acesso apenas às coleções e operações necessárias para o sistema funcionar. O RBAC organiza isso por meio de papéis e permissões. Se a aplicação receber privilégios demais e for comprometida, alguém poderá consultar informações indevidas, modificar registros ou até apagar dados que não deveria. Por isso, usamos contas separadas e permissões mínimas. Uma forma de comprovar essa separação é mostrar os papéis configurados e testar que a conta da aplicação não consegue executar uma ação administrativa.

## 7. Considere uma API que aceite filtros MongoDB enviados diretamente pelo cliente. Explique como operadores como $ne ou $where podem ser abusados e como a aplicação deve validar os filtros.

O problema é deixar o cliente enviar um filtro que o MongoDB execute sem controle. Um atacante pode usar operadores como $ne para mudar o sentido de uma comparação e tentar contornar uma verificação, ou $where para introduzir uma condição de consulta perigosa. Para evitar isso, a aplicação precisa validar os tipos dos valores, aceitar apenas os campos e operadores realmente necessários e montar o filtro no servidor. Por exemplo, se a API espera um nome como texto, ela não deve aceitar no lugar dele um objeto com operadores MongoDB. O teste de segurança consiste em enviar uma entrada inesperada e verificar que ela seja rejeitada.

## 8. Por que utilizar JSON Schema em um banco orientado a documentos considerado flexível? Relacione a resposta com integridade, qualidade dos dados e segurança.

Embora o MongoDB permita documentos flexíveis, isso não significa que qualquer informação deva ser aceita. O JSON Schema ajuda a definir quais campos são obrigatórios, quais tipos de dados são permitidos e quais regras os documentos precisam seguir. Por exemplo, um pedido pode exigir um identificador, um valor numérico e um status válido. Isso melhora a qualidade e a integridade dos dados, além de reduzir a entrada de informações inesperadas que poderiam provocar erros na aplicação. No laboratório, a evidência é tentar inserir um documento inválido e verificar que o banco o rejeita. Essa validação complementa, mas não substitui, os controles de acesso e a validação da aplicação.

## 9. Descreva como bindIp, firewall e TLS se complementam para proteger o MongoDB. Explique por que criptografia em trânsito não substitui controle de rede.

O bindIp define em quais interfaces de rede o MongoDB aceita conexões. O firewall restringe quais máquinas podem alcançar o serviço. Já o TLS criptografa os dados transmitidos entre a aplicação e o banco. Esses controles se complementam porque protegem partes diferentes da conexão. Mesmo com TLS, deixar a porta do MongoDB acessível para qualquer origem continua aumentando o risco de tentativas de acesso indevido. Ou seja, criptografar a comunicação não significa autorizar todas as conexões. Para demonstrar a proteção, podemos mostrar a configuração do bindIp, as regras de rede e uma conexão usando TLS.

## 10. Após concluir o laboratório NoSQL, identifique três riscos que ainda podem permanecer mesmo com autenticação, TLS, RBAC e backup configurados. Proponha controles adicionais.

Mesmo com esses recursos, ainda existem riscos. O primeiro é o roubo de credenciais: alguém pode conseguir uma senha válida; para reduzir isso, devemos proteger e trocar os segredos, além de limitar os privilégios. O segundo é uma falha na aplicação, como NoSQL Injection, que pode permitir consultas indevidas; para evitá-la, precisamos validar as entradas e montar os filtros com segurança. O terceiro é descobrir que o backup está corrompido ou não restaura os dados quando necessário; por isso, devemos testar o restore periodicamente e manter cópias protegidas. Esses exemplos mostram o risco residual: a segurança reduz a chance e o impacto dos problemas, mas não elimina todos eles.
