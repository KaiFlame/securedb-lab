# Roteiro de apresentação

1. **Vou mostrar o cenário.** Começo pelo diagrama. Explico que usamos dados fictícios, que o painel roda no meu computador e que os bancos ficam em uma rede interna do Docker. Mostro o ENV-01 para comprovar a configuração.
2. **Vou demonstrar o PostgreSQL.** Abro os pedidos com a conta da Aurora e depois com a da Vértice. Comparo as duas listas e mostro o teste em que um pedido aparece para a Vértice, mas fica fora do acesso da Aurora. Explico como o próprio banco aplica a política por linha.
3. **Vou demonstrar o MongoDB.** Abro o catálogo e os perfis. Uso um exemplo de documento para mostrar que o MongoDB aceita os campos válidos e rejeita uma gravação fora do esquema. Em seguida, mostro que a conta da aplicação tem acesso às coleções necessárias e recebe uma negativa ao tentar administrar usuários.
4. **Vou mostrar a conexão e a recuperação.** Aponto as evidências de TLS nos dois bancos e um evento de auditoria no PostgreSQL. Depois mostro que restauramos cada backup em uma base separada e conferimos os dados recuperados. Explico que o tempo medido cobre a restauração dos dados do teste.
5. **Vou apresentar os simuladores.** Explico o que sustentou as notas de governança e IAM. Digo que o cenário anterior ficou sem registro e que os valores de continuidade foram usados como hipótese didática. Mostro o plano de evolução e as ações prioritárias.
6. **Vou encerrar com os resultados e as questões.** Mostro quais controles foram comprovados neste Mac, quais têm evidência de uma execução anterior e quais ainda precisam de verificação local. Uso as respostas dissertativas para ligar os conceitos aos exemplos que acabei de demonstrar.

Para me localizar durante a apresentação, consulto as capturas e os resultados em `evidencias/entrega/macos_local/` e os simuladores em `evidencias/simuladores/`. As senhas das contas fictícias ficam no arquivo local `.local/ACESSO_LOCAL.txt`.
