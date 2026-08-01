# Modelo de dados

Modelo conceitual aprovado para PostgreSQL e limites de persistência.

> Origem: documento mestre v0.12. As numerações originais foram mantidas para rastreabilidade.

### Modelo de dados PostgreSQL aprovado



#### Diretrizes gerais



- haverá um único banco PostgreSQL compartilhado pelas empresas;

- todas as tabelas empresariais terão `company_id` obrigatório;

- restrições únicas incluirão o escopo da empresa quando aplicável;

- autorização no Django será reforçada por Row-Level Security no PostgreSQL;

- ausência de contexto válido de empresa produzirá negação por padrão;

- identificadores públicos serão UUIDs;

- datas e horas serão armazenadas em UTC com `timestamptz`;

- registros mutáveis terão coluna de versão para concorrência otimista;

- estados textuais terão restrições também no banco;

- JSON será usado para snapshots e payloads versionados, não para substituir relações estruturadas.



#### Identidade e empresas



Tabelas conceituais:



- `users`;

- `companies`;

- `memberships`;

- `invitations`;

- `machines`;

- `machine_sessions`;

- `terms_versions`;

- `terms_acceptances`.



Keycloak será a autoridade de identidade, senha e sessão. `users` conterá apenas a projeção necessária ao domínio.



#### Clientes e projetos



Tabelas conceituais:



- `clients`;

- `projects`;

- `project_accesses`.



Regras:



- não haverá Proprietário individual por projeto;

- `project_accesses` representará somente atribuições de Administradores;

- nomes terão valor original e normalizado;

- unicidade será aplicada por empresa ou cliente;

- arquivamento usará `archived_at`.



#### Catálogo



Tabelas conceituais:



- `media_files`: identidade lógica;

- `file_versions`: versões e substituições de conteúdo;

- `drive_objects`: representação física no Drive;

- `metadata_versions`: histórico funcional;

- `tags`;

- `file_tags`.



Regras:



- arquivo lógico será separado da versão física;

- substituição preservará versões anteriores;

- caminho local completo permanecerá somente no SQLite do agente;

- PostgreSQL armazenará máquina, dispositivo e referência opaca da origem.



#### Uploads e comandos



Tabelas conceituais:



- `upload_batches`;

- `upload_items`;

- `upload_attempts`;

- `upload_checkpoints`;

- `task_leases`;

- `commands`.



Identificadores de sessões retomáveis serão criptografados e não aparecerão em auditoria ou respostas comuns.



#### Aprovações e downloads



Tabelas conceituais:



- `approval_requests`;

- `approval_decisions`;

- `download_requests`;

- `download_items`.



Solicitação e decisão serão separadas para preservar recusas, expirações e novas solicitações.



#### Drive e integrações



Tabelas conceituais:



- `drive_accounts`;

- `drive_change_cursors`;

- `drive_objects`;

- `integration_executions`;

- `outbox_messages`;

- `inbox_messages`.



Refresh tokens e outros segredos serão criptografados antes da persistência. Chaves de criptografia ficarão fora do banco.



#### Notificações



Tabelas conceituais:



- `notifications`;

- `notification_recipients`;

- `notification_deliveries`;

- `notification_reads`.



Criação, tentativa, entrega e leitura serão estados independentes.



#### Auditoria



- `audit_events` será imutável;

- manterá estado anterior e posterior quando aplicável;

- registrará empresa, usuário, máquina e correlação;

- poderá ser particionada por data conforme o volume;

- não poderá ser atualizada ou excluída pela aplicação;

- identificadores pessoais serão criptografados;

- busca exata de identificadores usará valor normalizado protegido por HMAC, nunca hash simples.



#### Limites de persistência



- operações comuns não apagarão registros fisicamente;

- arquivamento e lixeira terão campos específicos;

- caminhos locais não serão centralizados;

- ORM Django ficará restrito aos adaptadores de persistência;

- repositórios converterão modelos Django em entidades do domínio;

- migrations serão pequenas, focadas e testadas.



#### Critérios de isolamento e segurança



- consulta sem empresa válida não poderá retornar dados empresariais;

- Administrador não poderá consultar projeto não atribuído;

- token, segredo ou URL retomável não poderá aparecer em logs;

- auditoria será imutável;

- perda do Redis não afetará estados persistidos;

- unicidade respeitará normalização e escopo empresarial.



