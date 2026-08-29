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



Tabelas implementadas neste incremento:



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

- `upload_checkpoints`.

As tabelas preservam conta e pasta de destino, versão física, ordem, tamanho, checksum,
tentativas numeradas e checkpoints monotônicos. Há no máximo uma conta ativa por empresa,
uma participação ativa por versão física e uma tentativa ativa por item.

Tabelas ainda conceituais:

- `task_leases`;

- `commands`.



Identificadores de sessões retomáveis são criptografados em
`upload_attempts.session_reference_ciphertext` e não aparecem em auditoria ou respostas
comuns. A exceção controlada é o endpoint exclusivo do agente, que entrega a URL
temporária após validar empresa, usuário, projeto e máquina.

Cada `upload_batch` deverá referenciar de forma imutável a `drive_account` escolhida
na criação. Trocar a conta ativa da empresa não poderá alterar lotes anteriores nem
permitir retomada em outra conta.

No agente, a migration SQLite v4 adiciona `upload_jobs`, identificada por `item_id`,
com `media_file_id`, caminho local, tentativa, tamanho, SHA-256, bytes confirmados,
estado e erro resumido. A tabela deliberadamente não possui coluna para URL de sessão,
token ou credencial.

O `drive_objects` existente foi ampliado pela migration `catalog.0006`: item de upload,
conta, pasta, nome, tamanho, SHA-256 e tipo MIME. A combinação conta/ID externo e o
vínculo único com o item impedem confirmação duplicada ou substituição silenciosa.



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

- `drive_folders`;

  Implementada com vínculo à conta e, quando aplicável, ao projeto; chave funcional
  idempotente por conta, ID da pasta no provedor, ID do pai, nome e timestamps. A
  restrição única `(account, folder_key)` impede duplicação lógica da árvore
  `Empresa/Projeto/AAAA.MM/DD/{Originais,Previews,Entregas}`;

- `drive_change_cursors`;

- `drive_objects`;

- `integration_executions`;

- `outbox_messages`;

- `inbox_messages`.



Refresh tokens e outros segredos serão criptografados antes da persistência. Chaves de criptografia ficarão fora do banco.

Contas desconectadas deverão conservar identidade e referências históricas sem
conservar credencial utilizável. A implementação atual possui apenas uma conta ativa
por empresa e deverá evoluir antes da criação dos lotes.



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



