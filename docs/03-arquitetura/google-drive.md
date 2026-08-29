# Integração com Google Drive

**Produto:** Gerenciador de Áudio Visual.

**Estado atual:** OAuth implementado e validado com conta Google real em 25 de
agosto de 2026. Estrutura idempotente de pastas implementada e validada no Drive real
em 26 de agosto de 2026. Histórico de contas, lotes, itens, tentativas e checkpoints
foram implementados em 28 de agosto. A criação, consulta e renovação segura da sessão
retomável e o envio direto em blocos pelo agente também estão implementados. O ensaio
real e os controles operacionais permanecem pendentes. A confirmação central do objeto
foi implementada e validada com gateway simulado.

Propriedade, OAuth, upload retomável, custos e limites do ambiente de testes.

> Origem: documento mestre v0.12. As numerações originais foram mantidas para rastreabilidade.

### Integração com Google Drive aprovada

#### Conta e propriedade

- Google Workspace e Drive Compartilhado serão obrigatórios;
- arquivos enviados pertencerão à organização;
- a aplicação não usará como armazenamento principal o `Meu Drive` de uma pessoa;
- contas adicionais poderão ser associadas futuramente por decisão de Proprietário.

No MVP, uma empresa terá uma conta Google ativa por vez. O Proprietário poderá
desconectar uma conta cheia e conectar outra. A troca afetará somente novos lotes:
arquivos existentes permanecerão na conta anterior e cada lote registrará a conta
de destino utilizada. Conta pessoal é permitida apenas para desenvolvimento;
Google Workspace e Drive Compartilhado continuam como objetivo de produção.

#### OAuth e credenciais

- o backend Django será a autoridade sobre as credenciais do Google;
- será solicitado inicialmente apenas o escopo `drive.file`;
- refresh tokens serão armazenados criptografados e nunca serão enviados ao agente;
- o agente não terá acesso à credencial OAuth central;
- n8n não armazenará a credencial principal do Google;
- segredos e tokens nunca aparecerão em logs, auditoria ou frontend.
- o backend usa Authorization Code, estado aleatório persistido como hash, validade
  de dez minutos e consumo único;
- refresh token e e-mail da conta são criptografados no PostgreSQL;
- somente Proprietário conecta ou desconecta a conta;
- desconectar elimina imediatamente a credencial local; revogação remota no Google
  permanece pendente no adaptador real.

#### Estrutura oficial implementada

```text
Gerenciador de Áudio Visual/
└── Empresa/
    └── Projeto/
        └── ANO.MÊS/
            └── DIA/
                ├── Originais/
                ├── Previews/
                └── Entregas/
```

Exemplo: `Gerenciador de Áudio Visual/Empresa/Projeto/2026.08/25/Originais`.
Ano, mês e dia usam zeros à esquerda. As pastas são criadas sob demanda e reutilizadas
pelo identificador do Drive. O PostgreSQL armazena os IDs, a conta, o projeto, a chave
funcional e o pai; nomes não são usados isoladamente como identidade. A operação é
serializada por conta e idempotente.

O modelo preserva contas históricas e impõe no máximo uma conta ativa por empresa.
Cada lote guarda imutavelmente a conta e as pastas escolhidas na criação. Desconectar
a conta remove suas credenciais locais e impede novas sessões para lotes associados.

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

#### Implementação atual do envio em blocos

- o backend cria, consulta e renova a sessão retomável;
- a referência da sessão é cifrada no PostgreSQL e descriptografada somente para a
  resposta exclusiva do agente;
- o agente localiza o arquivo pelo `media_file_id`; caminhos permanecem no SQLite;
- o comando `UPLOAD_FILE` usa o item de upload como `resource_id`;
- o agente valida tamanho e SHA-256 antes do primeiro bloco;
- o bloco padrão possui 8 MiB e sempre é múltiplo de 256 KiB;
- somente o último bloco pode ser menor;
- `308 Resume Incomplete` avança pelo cabeçalho `Range` confirmado pelo Drive;
- `200` ou `201` conclui o transporte e encaminha o item para verificação;
- `404` ou `410` invalida a sessão, cria nova tentativa e reinicia pelo ponto que o
  Drive confirmar para a nova sessão;
- falha de rede grava `INTERRUPTED` no SQLite e mantém o comando retomável;
- antes de cada bloco, o agente consulta o controle central do item;
- `PAUSE_REQUESTED` e `CANCEL_REQUESTED` são aplicados entre blocos, preservando o
  último byte confirmado; `PAUSED` permanece estável até retomada explícita;
- a retomada devolve o item a `READY`, sem criar lote ou objeto duplicado;
- a URL temporária existe apenas em memória e nunca entra no SQLite, no resultado do
  comando, na auditoria ou no frontend.

O SQLite v4 armazena `item_id`, `media_file_id`, caminho local, `attempt_id`, tamanho,
SHA-256, bytes confirmados, estado e código resumido da falha. PostgreSQL permanece
como fonte central do lote e Google Drive como fonte dos bytes efetivamente aceitos.

Regras:

- blocos respeitarão os múltiplos exigidos pela API do Drive;
- ponto de retomada nunca será presumido;
- sessão expirada será substituída com proteção contra duplicidade;
- autorização temporária da sessão será tratada como segredo;
- espera exponencial com variação aleatória permanece pendente;
- falta de espaço produzirá `AGUARDANDO_ESPACO_DRIVE`;
- cota diária atingida produzirá `AGUARDANDO_COTA_DRIVE`;
- arquivo acima de 5 TB não será enviado e receberá `NAO_SUPORTADO_PELO_DRIVE`;
- arquivo não suportado pelo Drive permanecerá preservado, organizado e catalogado localmente.

Após o último bloco, o agente entrega somente o ID do objeto. O backend consulta o
Drive, valida lixeira, tamanho, pasta, nome e SHA-256 quando disponível, persiste o
`drive_object` e somente então sincroniza o catálogo. A confirmação é idempotente.

O ensaio real com arquivo descartável, interrupção e retomada foi aprovado em 29 de
agosto de 2026. Pausa, retomada, cancelamento e mensagens operacionais específicas
estão implementados. Permanecem pendentes os ensaios reais dos limites de cota e espaço.

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


