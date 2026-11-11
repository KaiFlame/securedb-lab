# Riscos residuais e limites

Este laboratório usa exclusivamente dados sintéticos. Seus controles demonstram cenários delimitados; não constituem uma certificação de segurança nem uma configuração pronta para produção.

| Risco residual | Impacto | Controle existente | Próxima medida |
|---|---|---|---|
| Backend comprometido altera o GUC de tenant | Leitura/escrita entre empresas SQL | RLS com USING e WITH CHECK; contexto vindo da sessão; parametrização | Identidades de banco por tenant ou contexto assinado, revisão de código e testes adicionais |
| Conta MongoDB de negócio acessa duas empresas | Exposição entre empresas após comprometimento da API | Filtros de tenant obrigatórios na API; RBAC por coleção | Credenciais/bases por empresa quando a fronteira exigir isolamento no SGBD |
| Host ou administrador comprometido | Controle de bancos, logs e chaves | Serviços de baixo privilégio e credenciais separadas | Hardening do host, PAM/MFA, gestão de segredos e segregação operacional |
| Backups e chave no mesmo host | Perda simultânea ou decriptação por invasor do host | AES-256-GCM, restauração em base separada, fingerprint | Offsite, imutabilidade e cofre externo para a chave |
| Backup sem agenda/PITR | RPO indefinido entre execuções manuais | Rotina reprodutível e tempos medidos | Agenda, retenção, alertas e PITR conforme BIA |
| MongoDB standalone durante escritas | Dump pode não representar um instante consistente | Comparação antes/depois; orientação para pausar escritas | Replica set e estratégia de backup consistente conforme a versão |
| Navegador em HTTP local | Cookie sem atributo Secure e canal local sem TLS | Bind 127.0.0.1, HttpOnly, SameSite Strict, CSRF e verificação de Origin | HTTPS de ponta a ponta e Secure antes de uso remoto |
| Logs modificáveis e cobertura limitada | Lacunas de investigação | Eventos da API, trigger SQL, logs de conexão/DDL | Centralização, retenção, imutabilidade e alertas; Community sem Enterprise audit |
| Sem MFA/SSO na aplicação | Acesso após furto de senha | Argon2id, sessão de duas horas e limitador local de login | Provedor OIDC/MFA; sessões e rate limiting distribuídos |
| Dependências e imagens envelhecem | Vulnerabilidades futuras | Versões registradas, lockfile, SCA e dependabot | Revalidar boletins e atualizar com testes; tags não são digests imutáveis |
| Rede de dados compartilhada no Compose | Movimento lateral após comprometimento de um contêiner | Rede interna sem publicação dos bancos; TLS e autenticação | Separar redes por banco e políticas de saída conforme necessidade |
| Subnet fixa colide com rede do host | Ambiente não inicia ou roteamento incorreto | Subnet explícita documentada | Ajustar conjuntamente Compose e pg_hba, e reexecutar a suíte |

Não há HA, failover, SIEM, replicação, KMS, WAF, auditoria Enterprise ou certificação ISO implementados. A verificação de rede do Compose depende de ENV-01; uma execução nativa em Windows não comprova esse item.

Os dumps incluem hashes de contas e sessões. Apenas a cópia cifrada é mantida em `.local/backups`; o material temporário claro é removido após a operação normal. Chaves privadas, credenciais e logs brutos não integram a entrega Git. Exclusão de arquivo temporário não equivale a apagamento forense do disco.
