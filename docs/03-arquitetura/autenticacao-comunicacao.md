# Autenticação e comunicação

Sessões do frontend e agente, comunicação agente–backend e segurança.

> Origem: documento mestre v0.12. As numerações originais foram mantidas para rastreabilidade.

### Autenticação aprovada

#### Frontend

- Keycloak será o provedor de identidade por OpenID Connect;
- o frontend usará Authorization Code com PKCE;
- tokens de acesso terão duração curta e renovação vinculada à sessão ativa;
- empresa, papel, projetos e permissões funcionais serão controlados pelo Django;
- o Keycloak será responsável por identidade, credenciais e sessões, não pelas regras de autorização do domínio.

#### Agente local

- o login será realizado no navegador padrão do sistema;
- o agente não exibirá nem capturará senha em formulário próprio;
- será usado Authorization Code com PKCE e retorno temporário somente por `localhost`;
- token de acesso ficará somente em memória;
- segredos locais necessários durante a sessão ficarão no cofre seguro do sistema operacional;
- senhas, tokens e credenciais do Drive nunca serão armazenados no SQLite;
- após reinício do computador, o agente descartará qualquer possibilidade de restauração automática e exigirá nova autenticação.

#### Sessão única

- Keycloak limitará cada usuário a uma sessão ativa;
- novo login encerrará a sessão anterior;
- frontend e agente poderão participar da mesma sessão autenticada;
- Django validará sessão, empresa e permissões antes de comandos sensíveis;
- bloqueio, saída da empresa ou perda de acesso impedirá novos comandos e interromperá operações no próximo bloco seguro.


### Comunicação agente–backend aprovada

- toda comunicação será iniciada pelo agente por HTTPS ou WebSocket seguro;
- nenhuma porta da máquina ficará exposta à internet;
- o WebSocket indicará presença, mudanças e existência de novos comandos;
- comandos serão persistidos no PostgreSQL e nunca dependerão exclusivamente do WebSocket;
- após receber um aviso, o agente buscará o comando completo pela API;
- cada comando terá identificador único, versão e chave de idempotência;
- agente confirmará recebimento e resultado de cada comando;
- progresso será enviado em intervalos controlados, sem persistir cada bloco transferido;
- queda do WebSocket ativará reconexão progressiva e consulta periódica pela API;
- reinício do agente preservará a fila SQLite, mas nenhuma tarefa continuará antes de nova autenticação quando também houver reinício do computador;
- a autorização temporária de upload do Drive será tratada como segredo e nunca aparecerá em logs;
- o binário continuará sendo enviado diretamente do agente ao Drive.


### Critérios de segurança da comunicação

- token revogado não poderá autorizar novos comandos;
- repetição de comando não poderá duplicar upload ou movimentação;
- perda de WebSocket não poderá causar perda de tarefa;
- credenciais não poderão aparecer em SQLite, logs, frontend ou auditoria;
- logout, bloqueio ou remoção de acesso deverão impedir novos blocos no próximo ponto seguro;
- frontend e agente nunca confiarão em permissões sem validação do backend.


