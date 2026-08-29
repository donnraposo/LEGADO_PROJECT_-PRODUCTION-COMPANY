# Contratos de API

Padrões REST, operações assíncronas, erros, paginação e evolução.

> Origem: documento mestre v0.12. As numerações originais foram mantidas para rastreabilidade.

### Contratos de API aprovados



#### Padrão geral



- REST sobre HTTPS;

- JSON em UTF-8;

- prefixo `/api/v1`;

- OpenAPI 3.1 como contrato oficial;

- autenticação Bearer por OIDC do Keycloak;

- empresa explícita na URL e sempre validada pelo caso de uso;

- Django REST Framework será somente adaptador de entrada;

- nenhum endpoint transportará grandes binários audiovisuais.



#### Grupos funcionais



- usuário e empresas: `/api/v1/me` e `/api/v1/companies`;

- clientes e projetos: recursos subordinados a `/api/v1/companies/{company_id}`;

- catálogo: arquivos, versões, histórico de metadados e tags;

- uploads: lotes, itens, pausa, retomada e cancelamento;

- aprovações: solicitações, decisões e expirações;

- downloads e lixeira: solicitações, itens, envio e restauração;

- agente: máquinas, presença, comandos, confirmações e progresso;

- integrações internas: namespace `/api/internal/v1`;

- webhooks externos: namespace `/api/webhooks/v1`.



APIs internas terão audiência e credenciais próprias e não aceitarão tokens comuns de usuários.



#### Google Drive implementado



- consulta da conexão: `GET /api/v1/drive/account`;

- desconexão pelo Proprietário: `DELETE /api/v1/drive/account`;

- início da autorização: `POST /api/v1/drive/oauth/authorization`;

- callback público processado pelo backend: `GET /api/v1/drive/oauth/callback`;

- criação ou reutilização da árvore diária: `POST /api/v1/drive/folders/ensure`.



O último endpoint recebe `project_id` e `date` e devolve o caminho funcional e os IDs
de `originais`, `previews` e `entregas`. Refresh token, access token e credenciais não
fazem parte das respostas.

#### Lotes de upload implementados

- listar e criar lote: `GET|POST /api/v1/upload-batches`;
- consultar lote com itens: `GET /api/v1/upload-batches/{batch_id}`;
- solicitar pausa, retomada ou cancelamento:
  `POST /api/v1/upload-batches/{batch_id}/control`;
- criar ou reutilizar tentativa: `POST /api/v1/upload-items/{item_id}/attempts`;
- registrar checkpoint monotônico: `PUT /api/v1/upload-attempts/{attempt_id}/checkpoint`;
- criar, reutilizar ou renovar sessão para o agente:
  `POST /api/v1/agent/upload-items/{item_id}/session`;
- consultar controle e confirmar estado aplicado:
  `GET|POST /api/v1/agent/upload-items/{item_id}/control`.

A criação exige chave de idempotência. Repetição com o mesmo conteúdo reutiliza o lote;
a mesma chave com conteúdo diferente retorna conflito. Os contratos não expõem tokens
nem referências de sessão retomável. A URL temporária aparece somente na resposta do
endpoint do agente, após validar a máquina vinculada ao lote.

O controle recebe `action`, `expected_version` e `idempotency_key`. A repetição da
mesma ação com a mesma chave devolve o estado já persistido; reutilizar a chave para
outra ação ou controlar versão desatualizada retorna conflito. Cancelamento preserva
o histórico e pausa não reduz `confirmed_bytes`.

As respostas de lote incluem `confirmed_bytes` e `progress_percent`; cada item expõe
os mesmos campos calculados a partir do checkpoint mais recente confirmado pelo Drive.
O catálogo informa `file_version_id` e `source_machine_id` para que o frontend forme
lotes somente com versões físicas pertencentes à mesma máquina.

O contrato exclusivo do agente recebe `machine_id` e devolve `attempt_id`, `item_id`,
`media_file_id`, URL temporária, tamanho, algoritmo/digest de checksum e bytes
confirmados. Não devolve caminho local. `201` indica sessão criada ou renovada; `200`
indica reutilização. Indisponibilidade do Google retorna `502` sem expor seu payload.

O comando central `UPLOAD_FILE` referencia o item em `resource_id`. Seu resultado
contém somente `upload_item_id` e `confirmed_bytes`; URL e caminho são proibidos.

- confirmar objeto após o último bloco:
  `POST /api/v1/agent/upload-attempts/{attempt_id}/complete`.

A confirmação recebe máquina e ID externo, consulta o Drive com a credencial central e
retorna `201` na primeira persistência ou `200` na repetição idempotente.



#### Operações assíncronas



- criação concluída imediatamente retornará `201 Created`;

- comando aceito para processamento retornará `202 Accepted`;

- resposta assíncrona conterá identificador e endereço de consulta da operação;

- operações longas terão recurso próprio de estado;

- cancelamento será comando explícito e não exclusão HTTP do histórico.



#### Idempotência e concorrência



- mutações críticas aceitarão `Idempotency-Key`;

- mesma chave e mesmo payload retornarão o resultado anterior;

- mesma chave e payload diferente retornarão conflito;

- recursos mutáveis fornecerão versão ou ETag;

- atualizações concorrentes usarão `If-Match`;

- versão desatualizada retornará `409 Conflict`;

- comandos terão identificação de correlação e rastreamento.



#### Tratamento de erros



- erros usarão `application/problem+json`;

- conterão tipo, título, status HTTP, código estável, descrição segura e rastreamento;

- erros de validação poderão incluir campos inválidos;

- respostas nunca revelarão tokens, caminhos locais completos, SQL ou stack trace.



Códigos iniciais previstos:



- `COMPANY_ACCESS_DENIED`;

- `PROJECT_ACCESS_DENIED`;

- `RESOURCE_VERSION_CONFLICT`;

- `IDEMPOTENCY_CONFLICT`;

- `UPLOAD_ALREADY_ACTIVE`;

- `DEVICE_NOT_AVAILABLE`;

- `DRIVE_QUOTA_EXCEEDED`;

- `FILE_NOT_SUPPORTED_BY_DRIVE`;

- `APPROVAL_REQUIRED`;

- `SESSION_REVOKED`.



#### Listas e busca



- paginação por cursor;

- respostas de coleção conterão `items` e `next_cursor`;

- ordenação será estável;

- filtros serão explícitos e documentados;

- haverá limite máximo por página;

- busca não aceitará SQL ou expressões arbitrárias.



#### Formatos



- UUID como texto;

- datas e horas em ISO 8601 UTC;

- tamanhos em bytes inteiros;

- checksums acompanhados do algoritmo;

- estados em valores textuais estáveis;

- valores monetários futuros usarão unidade mínima inteira.



#### Evolução



- mudanças compatíveis poderão entrar em `v1`;

- mudanças incompatíveis exigirão `v2`;

- novos campos serão inicialmente opcionais;

- APIs depreciadas terão prazo e aviso documentados;

- clientes do frontend e agente serão gerados a partir do OpenAPI;

- código gerado ficará isolado e não conterá regras de negócio.



#### Critérios de contrato



- acesso negado não revelará existência de recurso de outra empresa;

- token de usuário não acessará API interna;

- repetição de mutação não duplicará efeito;

- concorrência não causará sobrescrita silenciosa;

- erros terão códigos estáveis e rastreamento;

- implementação deverá corresponder ao OpenAPI;

- endpoints não receberão nem devolverão grandes binários audiovisuais.



