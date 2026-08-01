# Integração com n8n

Responsabilidades permitidas, proibições, workflows e contratos com Django.

> Origem: documento mestre v0.12. As numerações originais foram mantidas para rastreabilidade.

### Responsabilidades e contratos do n8n aprovados



#### Responsabilidades permitidas



- enviar e-mails e notificações externas;

- montar resumos diários;

- executar lembretes de aprovação;

- acionar automações posteriores ao upload;

- coordenar integrações externas leves;

- solicitar ao Django uma conciliação do Drive;

- registrar no backend o resultado de uma integração.



#### Proibições



- n8n não alterará diretamente o PostgreSQL;

- n8n não decidirá permissões, aprovações ou estados do domínio;

- n8n não armazenará credenciais do Google Drive;

- n8n não transportará arquivos audiovisuais;

- n8n não executará exclusões sem comando autorizado pelo Django;

- n8n não substituirá Celery nas tarefas transacionais;

- n8n não será a fonte oficial da auditoria;

- nenhuma regra indispensável ao produto existirá apenas em um workflow.



#### Workflows iniciais



- `critical-alert`: alertas críticos imediatos;

- `approval-reminder`: lembretes de aprovação e expiração;

- `daily-digest`: agrupamento de eventos não críticos;

- `post-upload`: automações posteriores à sincronização;

- `drive-account-alert`: falta de espaço, cota ou desconexão;

- `reconciliation-request`: solicitação de verificação ao Django;

- `integration-result`: comunicação de sucesso ou falha externa.



#### Contratos com Django



- Django persistirá a mudança de domínio e o evento de saída na mesma transação;

- Celery entregará eventos ao n8n;

- n8n autenticará na API interna com credencial de serviço do Keycloak;

- cada evento conterá identificador, tipo, versão, empresa, recurso, data e correlação;

- repetição do mesmo identificador não poderá repetir o efeito;

- payloads não conterão tokens, caminhos locais ou dados desnecessários;

- n8n retornará somente resultado, referência externa e motivo de falha;

- auditoria permanente permanecerá no Django;

- histórico operacional do n8n terá retenção limitada;

- workflows serão exportados e versionados manualmente em repositório privado;

- auditorias periódicas verificarão webhooks desprotegidos, credenciais inutilizadas e nós arriscados.



