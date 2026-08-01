# Integração com Google Drive

Propriedade, OAuth, upload retomável, custos e limites do ambiente de testes.

> Origem: documento mestre v0.12. As numerações originais foram mantidas para rastreabilidade.

### Integração com Google Drive aprovada

#### Conta e propriedade

- Google Workspace e Drive Compartilhado serão obrigatórios;
- arquivos enviados pertencerão à organização;
- a aplicação não usará como armazenamento principal o `Meu Drive` de uma pessoa;
- contas adicionais poderão ser associadas futuramente por decisão de Proprietário.

#### OAuth e credenciais

- o backend Django será a autoridade sobre as credenciais do Google;
- será solicitado inicialmente apenas o escopo `drive.file`;
- refresh tokens serão armazenados criptografados e nunca serão enviados ao agente;
- o agente não terá acesso à credencial OAuth central;
- n8n não armazenará a credencial principal do Google;
- segredos e tokens nunca aparecerão em logs, auditoria ou frontend.

#### Escopo funcional

- somente arquivos enviados pela aplicação serão gerenciados;
- arquivos desconhecidos adicionados manualmente ao Drive não serão descobertos ou importados;
- alterações externas em arquivos já gerenciados continuarão sendo detectadas e reconciliadas;
- mudança externa nunca provocará ação destrutiva automática.

#### Upload retomável

1. backend valida usuário, empresa, projeto, arquivo e disponibilidade da conta;
2. backend cria ou localiza a estrutura de pastas;
3. backend inicia uma sessão retomável no Drive;
4. agente recebe somente a autorização temporária da sessão;
5. agente envia blocos diretamente ao Drive;
6. depois de interrupção, agente consulta o último byte confirmado;
7. backend valida identificador, tamanho, checksum e metadados finais;
8. somente após consistência completa o catálogo muda para `SINCRONIZADO`.

Regras:

- blocos respeitarão os múltiplos exigidos pela API do Drive;
- ponto de retomada nunca será presumido;
- sessão expirada será substituída com proteção contra duplicidade;
- autorização temporária da sessão será tratada como segredo;
- erros temporários usarão espera exponencial com variação aleatória;
- falta de espaço produzirá `AGUARDANDO_ESPACO_DRIVE`;
- cota diária atingida produzirá `AGUARDANDO_COTA_DRIVE`;
- arquivo acima de 5 TB não será enviado e receberá `NAO_SUPORTADO_PELO_DRIVE`;
- arquivo não suportado pelo Drive permanecerá preservado, organizado e catalogado localmente.

#### Conciliação

- notificações do Drive indicarão apenas que existem mudanças;
- backend consultará o log de alterações antes de modificar o catálogo;
- Celery executará conciliação assíncrona e periódica;
- estado anterior e estado atual serão comparados;
- identificadores de mudança serão persistidos para retomada;
- conciliação completa periódica cobrirá notificações perdidas.


### Estratégia de custos e evolução comercial

#### Fase inicial

- a plataforma atenderá inicialmente uma única produtora;
- desenvolvimento e validação usarão somente componentes gratuitos ou executados localmente;
- n8n será usado apenas em edição comunitária, de forma interna e sem exposição da interface a clientes;
- recursos exclusivos de planos pagos do n8n não poderão se tornar dependências obrigatórias;
- workflows serão exportados e versionados manualmente em repositório privado;
- PostgreSQL, Redis, Keycloak, Celery e demais componentes livres serão executados localmente em containers;
- e-mails de desenvolvimento usarão capturador SMTP local;
- miniaturas e objetos de desenvolvimento usarão inicialmente um adaptador de sistema de arquivos local;
- armazenamento S3 compatível será opcional e substituível;
- existe uma conta pessoal paga do Google Drive disponível para testes de integração;
- a conta pessoal será limitada a uma pasta isolada criada para o projeto;
- essa conta permitirá validar OAuth, upload retomável, metadados, movimentação, lixeira e conciliação dos arquivos gerenciados;
- testes comuns continuarão independentes do Google Drive e usarão adaptadores locais;
- testes específicos de Drive Compartilhado permanecerão pendentes até existir uma conta Google Workspace adequada.

#### Adaptadores substituíveis

- o domínio e os casos de uso dependerão de contratos abstratos, nunca diretamente de n8n ou Google Drive;
- haverá adaptador n8n substituível por Celery ou outra tecnologia;
- haverá adaptador real do Google Drive e adaptador local de desenvolvimento;
- o adaptador local simulará pastas, sessões retomáveis, falhas, cotas e estados necessários aos testes;
- somente testes específicos de integração exigirão uma conta real do Google Workspace quando ela estiver disponível;
- o adaptador real poderá usar temporariamente a conta pessoal de testes sem alterar os contratos internos;
- nenhuma regra de negócio poderá existir exclusivamente em workflow do n8n.

#### Comercialização futura

- o projeto será preparado para atender outras produtoras no futuro;
- antes da entrada da primeira produtora externa haverá revisão obrigatória de licenças, custos, contratos e conformidade;
- nessa revisão será decidido entre adquirir licença adequada do n8n ou substituí-lo por uma implementação permitida;
- nenhuma produtora externa poderá acessar o editor, workflows ou credenciais do n8n antes dessa decisão;
- custos futuros de Google Workspace, armazenamento, hospedagem, e-mail e observabilidade serão tratados na fase de planejamento de produção.


### Limitações do ambiente de testes do Drive

- o Drive pessoal não será tratado como equivalente ao Drive Compartilhado de produção;
- propriedade organizacional, permissões herdadas e comportamentos exclusivos de Drives Compartilhados exigirão validação posterior;
- nenhum arquivo pessoal existente será descoberto, importado, movido ou alterado;
- o escopo continuará limitado aos arquivos e pastas criados ou explicitamente disponibilizados à aplicação;
- testes destrutivos ficarão restritos aos recursos criados dentro da pasta isolada do projeto.


