# Decisões e continuidade

Protocolo, registro de decisões, instruções de retomada e histórico do documento.

> Origem: documento mestre v0.12. As numerações originais foram mantidas para rastreabilidade.

## 2. Protocolo obrigatório de continuidade

O agente responsável pelo projeto deve atuar primeiro como **Arquiteto de Software Sênior e Tech Lead**.

### Ordem obrigatória

1. compreender o problema;
2. concluir as regras de negócio;
3. discutir e comparar tecnologias;
4. propor a arquitetura técnica detalhada;
5. definir estrutura do projeto e modelo de dados;
6. preparar roadmap, testes e critérios de aceite;
7. solicitar aprovação explícita;
8. implementar somente após aprovação.

Discussão ou planejamento não autorizam implementação.

Antes da aprovação explícita da implementação, não se deve:

- escrever código;
- criar a estrutura do software;
- instalar dependências;
- modificar banco de dados;
- iniciar infraestrutura;
- escolher tecnologias como decisão definitiva sem discussão;
- alterar uma decisão arquitetural aprovada sem explicar o impacto e receber nova aprovação.

Este documento foi criado por autorização expressa do usuário para permitir a continuidade do projeto em outro computador. Essa autorização não inclui implementação de código.

---


## 39. Registro resumido das decisões

| Decisão | Estado |
|---|---|
| Documentação fragmentada por categorias, com índice central | APROVADO |
| Regras de negócio antes das tecnologias | APROVADO |
| Frontend online | APROVADO |
| Arquitetura híbrida | APROVADO |
| Agente envia binário diretamente ao Drive | APROVADO |
| n8n orquestra sem transportar arquivos grandes | APROVADO |
| PostgreSQL armazena metadados, estados e auditoria | APROVADO |
| Organização local por Cliente/Projeto/Ano/Mês/Dia | APROVADO |
| Árvore do Drive por Empresa/Projeto/AAAA.MM/DD/categoria | APROVADO E VALIDADO |
| Data da câmera, com fallback do sistema de arquivos | APROVADO |
| Prévia obrigatória | APROVADO |
| Nunca apagar arquivos físicos | APROVADO |
| Upload retomável e verificação de integridade | APROVADO |
| Várias empresas, usuários e máquinas | APROVADO |
| Papéis Proprietário e Administrador | APROVADO |
| Uma conta pode participar de várias empresas | APROVADO |
| Cadastro público de conta e empresa | APROVADO |
| Sem aprovação prévia de máquina | APROVADO |
| Login obrigatório antes de qualquer operação | APROVADO |
| Uma sessão por usuário | APROVADO |
| Sessão válida até logout ou revogação | APROVADO |
| Sem autenticação em dois fatores nesta fase | APROVADO |
| Administrador acessa somente projetos permitidos | APROVADO |
| Proprietário acessa todos os projetos | APROVADO |
| Administrador pode enviar à lixeira | APROVADO |
| Somente Proprietário pode restaurar | APROVADO |
| Substituição por Administrador exige aprovação em até 48 horas | APROVADO |
| Auditoria funcional permanente e exclusiva dos Proprietários | APROVADO |
| Alertas internos e por e-mail para Proprietários | APROVADO |
| Alterações externas sincronizam o catálogo | APROVADO |
| Tags genéricas e personalizadas | APROVADO |
| Tags, descrições e observações somente no catálogo | APROVADO |
| Download individual, em lote, estruturado ou ZIP | APROVADO |
| Regras de negócio complementares | APROVADO |
| Frontend React, TypeScript e Vite | APROVADO |
| Backend Python e Django | APROVADO |
| Agente local Python e PySide6 | APROVADO |
| PostgreSQL, Redis, Celery e Channels | APROVADO |
| Keycloak via OpenID Connect | APROVADO |
| Clean Architecture, Clean Code e SOLID | APROVADO |
| Uma classe por arquivo | APROVADO |
| Autenticação com Keycloak, OIDC e PKCE | APROVADO |
| Comunicação segura agente–backend | APROVADO |
| Google Workspace e Drive Compartilhado | APROVADO |
| Escopo OAuth `drive.file` | APROVADO |
| Gerenciar somente arquivos enviados pela aplicação | APROVADO |
| Arquivos acima de 5 TB como `NAO_SUPORTADO_PELO_DRIVE` | APROVADO |
| Integração OAuth e upload retomável no Drive | APROVADO |
| Uma produtora na fase inicial | APROVADO |
| Comercialização futura para outras produtoras | PLANEJADO |
| Desenvolvimento inicial sem serviços pagos obrigatórios | APROVADO |
| n8n Community somente para uso interno inicial | APROVADO |
| Adaptadores substituíveis para n8n e Drive | APROVADO |
| Drive pessoal pago para integração em pasta isolada | APROVADO |
| Validação futura em Drive Compartilhado | PENDENTE |
| Responsabilidades e contratos do n8n | APROVADO |
| Filas, retomada, concorrência e idempotência | APROVADO |
| Modelo de dados PostgreSQL | APROVADO |
| Contratos de API e tratamento de erros | APROVADO |
| Monorepo para backend, agente, frontend, contratos e infraestrutura | APROVADO |
| Backend como monólito modular Django | APROVADO |
| Organização por domínio funcional e depois por camada | APROVADO |
| Comunicação entre módulos por casos de uso, contratos ou eventos | APROVADO |
| Proibição de acesso direto ao ORM de outro módulo | APROVADO |
| Estrutura do repositório e módulos | APROVADO |
| Dados PostgreSQL externos ao ciclo de vida dos containers | APROVADO |
| Volume persistente estável e obrigatório por ambiente | APROVADO |
| Bloqueio da implantação quando o volume esperado estiver ausente | APROVADO |
| Migrations pelo padrão expandir, migrar e contrair | APROVADO |
| Backup anterior a mudanças críticas | APROVADO |
| Restauração controlada, nunca sobre banco existente automaticamente | APROVADO |
| Backup físico e WAL/PITR para produção comercial futura | PLANEJADO |
| Demais detalhes da arquitetura técnica | PENDENTE |
| Implementação incremental | AUTORIZADA EM 01/08/2026 |
| Movimentação local sem substituição e com checkpoint por arquivo | APROVADO |
| Ingestão do agente idempotente e sem caminho local no backend | APROVADO |

---


## 40. Instrução para outra IA ou novo responsável

Ao retomar este projeto:

1. leia o índice principal, o estado e apenas os blocos relacionados à tarefa;
2. não reinicie a descoberta já registrada;
3. trate decisões marcadas como APROVADO como requisitos vigentes;
4. não altere essas decisões sem explicar impacto e receber aprovação;
5. considere concluídas as regras de negócio da seção 37;
6. considere aprovada a stack registrada na seção 35;
7. considere aprovadas a autenticação e a comunicação agente–backend registradas na seção 35;
8. considere aprovada a integração com o Drive registrada nas seções 22 e 35;
9. considere aprovadas as responsabilidades e contratos do n8n registrados na seção 35;
10. considere aprovadas as regras de filas, retomada, concorrência e idempotência da seção 35;
11. considere aprovado o modelo de dados PostgreSQL registrado na seção 35;
12. considere aprovados os contratos de API registrados na seção 35;
13. considere aprovada a estrutura de monorepo, módulos e dependências entre camadas;
14. considere aprovadas a persistência, a esteira de atualização, as migrations seguras e a recuperação;
15. continue pela composição Docker, exposição de rede, hospedagem e observabilidade;
16. documente cada decisão no bloco temático correspondente e neste registro;
17. mantenha o estado, a próxima etapa e o histórico atualizados;
18. não escreva código nem crie estrutura de implementação antes de aprovação explícita.

---


## 41. Histórico do documento

As entradas abaixo registram o estado existente na data de cada decisão. Para o
estado atual, prevalecem a entrada mais recente e os documentos de entrega.

### 31 de agosto de 2026 — versão 0.45

- incluído o botão `Selecionar HD` para análise de uma mídia inteira;
- cada nova análise exige a escolha explícita da mídia ou pasta de destino;
- último destino mantido somente como sugestão, sem reutilização silenciosa;
- destino dentro da origem bloqueado para impedir processamento recursivo;
- suíte do agente ampliada para 41 testes, com Ruff aprovado.

### 31 de agosto de 2026 — versão 0.44

- botão `Entrar` renomeado para `LOGIN` no agente;
- removida a seleção de destino do fluxo operacional diário;
- pasta-base configurada uma vez, persistida localmente e alterável pelo menu de configurações;
- estrutura `Cliente/Projeto/Ano/Mês/Dia` criada automaticamente após a confirmação;
- prévia do destino permanece obrigatória e nenhuma sobrescrita foi autorizada;
- SQLite evoluído para v5 e suíte do agente ampliada para 39 testes.

### 31 de agosto de 2026 — versão 0.43

- bloqueio de associação durante canal aberto passa a encerrar o WebSocket no próximo evento;
- documentação corrente consolidada com 66 testes backend, 37 do agente e 21 do frontend;
- Fase 6 passa a implementada, aguardando ensaios reais de falha;
- Fase 8 concentra E2E visual, ensaio de backup/restauração, instalador e publicação;
- release permanece candidata local e não publicada.

### 30 de agosto de 2026 — versão 0.42

- aprovado WebSocket apenas como aviso, mantendo a API como fonte de verdade e polling
  automático como contingência;
- ingresso do canal definido como efêmero, de uso único e vinculado à associação ativa,
  sem expor token OIDC na URL;
- reconciliação de upload definida pelo checkpoint remoto do Drive, persistido no
  PostgreSQL e aplicado ao SQLite antes do próximo bloco;
- backup exige manifesto SHA-256 e restauração exige confirmação literal;
- publicação externa da release permanece dependente de autorização específica.

### 30 de agosto de 2026 — versão 0.41

- status internos de upload permanecem em inglês nos contratos, banco e agente;
- painel traduz os estados para português por um mapeamento centralizado;
- valores desconhecidos não expõem códigos técnicos ao usuário.

### 29 de agosto de 2026 — versão 0.40

- login do usuário definido como única ação necessária para operar o agente;
- removida a conexão, aprovação e liberação manual de máquinas;
- UUID da instalação e heartbeat permanecem apenas como mecanismos técnicos de origem,
  roteamento, retomada e idempotência;
- autorização permanece vinculada ao usuário, à empresa e aos projetos vigentes;
- remoção ou bloqueio do usuário interrompe o acesso de todas as instalações associadas;
- falhas transitórias da sessão técnica passam a ter repetição automática e invisível.

### 29 de agosto de 2026 — versão 0.39

- concluídos controles operacionais de pausa, retomada e cancelamento no próximo bloco seguro;
- estado `PAUSED` permanece estável até retomada explícita;
- controles usam versão esperada e chave idempotente, sem excluir histórico;
- progresso central permanece monotônico e baseado nos bytes confirmados pelo Drive;
- falhas de internet, autenticação, cota, disco e integridade receberam códigos estáveis
  e mensagens simples no painel;
- 64 testes backend, 36 testes do agente, 5 testes frontend, TypeScript e build aprovados;
- backend e frontend reconstruídos, migrados e confirmados saudáveis.

### 29 de agosto de 2026 — versão 0.38

- implementado painel de lotes por projeto, data, categoria e arquivos catalogados;
- máquina derivada da versão física e lotes com múltiplas máquinas bloqueados;
- progresso geral e individual exposto por bytes confirmados e percentual;
- polling de dois segundos restrito a lotes ativos, com restauração após recarga;
- chave idempotente reutilizada durante repetição da mesma tentativa de criação;
- erros técnicos convertidos em mensagens simples no frontend;
- estilos consolidados em variáveis CSS para paleta, estados, superfícies, sombras,
  raios e dimensões estruturais;
- 63 testes backend, Ruff, 5 testes frontend, TypeScript e build aprovados.
- controles de lote usam `expected_version` e chave idempotente, sem exclusão do histórico;
- pausa e cancelamento são aplicados somente entre blocos, preservando o bloco em trânsito;
- Drive continua sendo a fonte dos bytes confirmados e checkpoints centrais não regridem;
- falhas operacionais normalizadas para internet, autenticação, cota, disco e integridade.

### 28 de agosto de 2026 — versão 0.37

- consolidada a conclusão do OAuth e da árvore idempotente do Google Drive;
- registrada a estrutura oficial
  `Gerenciador de Áudio Visual/Empresa/Projeto/AAAA.MM/DD/{Originais,Previews,Entregas}`;
- registrado o ensaio real de 26 de agosto: oito pastas ativas, com um pai cada, e
  segunda execução sem duplicação;
- diferenciada a organização local por cliente da estrutura remota por empresa;
- atualizados contrato, modelo de dados, plano de testes, continuidade e roadmap;
- definida como próxima fatia a persistência de contas históricas, lotes, itens,
  tentativas e checkpoints, seguida pelo upload retomável direto agente–Drive.
- implementada em 28 de agosto de 2026 a persistência histórica de contas, lotes
  vinculados à conta e às pastas, itens, tentativas e checkpoints monotônicos;
- criação de lote protegida por chave de idempotência e conflito de conteúdo;
- sessão retomável e transporte direto agente–Drive foram definidos como o incremento seguinte;
- implementada a sessão retomável exclusiva do agente, com URL cifrada, reutilização,
  expiração auditável e renovação em nova tentativa;
- envio dos blocos e ensaio da sessão no Drive real permanecem pendentes.
- implementado o envio direto em blocos pelo comando `UPLOAD_FILE`, com blocos de
  8 MiB, checkpoint SQLite v4 e URL retomável somente em memória;
- naquele ponto, ensaio real e confirmação do objeto ainda permaneciam pendentes.
- caminhos locais são resolvidos no agente pelo `media_file_id` e não integram o
  comando `UPLOAD_FILE` nem o contrato da sessão;
- Google Drive prevalece sobre SQLite e PostgreSQL quanto aos bytes confirmados;
- resposta `308` cria checkpoint, `404/410` renova sessão e `200/201` conclui transporte.
- confirmação final consulta o Drive pelo backend e valida pasta, nome, tamanho,
  lixeira e SHA-256 antes de persistir o objeto e sincronizar o catálogo;
- migration `catalog.0006` amplia `drive_objects` sem criar representação concorrente;
- ensaio real tentado em 28 de agosto não criou objeto devido a falha de DNS do Docker.
- ensaio real aprovado em 29 de agosto: DNS externo operacional no backend Docker,
  arquivo de 17 MiB retomado após 8 MiB e objeto confirmado por ID, tamanho e SHA-256;
- mantida a resolução DNS padrão do Docker, pois a reativação dos containers eliminou
  a indisponibilidade e os endpoints Google resolveram sem configuração fixa.

### 25 de agosto de 2026 — versão 0.36

- relida e consolidada a documentação temática, arquitetural e operacional;
- oficializado `Gerenciador de Áudio Visual` como nome do produto em documentos e READMEs;
- registrada a autorização OAuth real concluída e removidas pendências antigas de credenciais;
- documentada a troca futura de conta Google: uma ativa por empresa e lote vinculado
  à conta de destino, sem mover arquivos já enviados;
- registrado que o modelo atual ainda não preserva histórico de contas anteriores;
- definida como próxima fatia a confirmação da árvore de pastas, seguida por
  persistência de pastas, lotes, tentativas e checkpoints;
- mantidos como pendentes upload real, retomada, cota, integridade e conciliação.

### 25 de agosto de 2026 — versão 0.35

- iniciada a implementação da Fase 6 pelo fluxo OAuth do Google Drive;
- mantido o escopo mínimo `drive.file` e a troca de código exclusivamente no backend;
- definido estado OAuth aleatório, armazenado como hash, válido por dez minutos e de uso único;
- definido refresh token criptografado e isolado por empresa;
- limitada conexão e desconexão ao Proprietário, mantendo consulta para membros;
- registrado que lotes e upload retomável são o próximo incremento e que o ensaio
  real depende das credenciais do Google Cloud.

### 25 de agosto de 2026 — versão 0.34

- frontend de upload incluído como parte obrigatória da Fase 6 e do aceite do MVP;
- Proprietário conectará a conta Google pelo frontend, mantendo OAuth e refresh token
  exclusivamente no backend;
- usuários autorizados poderão criar e acompanhar lotes, visualizar progresso geral e
  individual e solicitar pausa, retomada ou cancelamento;
- controles serão persistidos e aplicados pelo agente no próximo bloco seguro;
- polling será usado inicialmente; WebSocket permanece planejado para a Fase 7;
- recarregar a página deverá recuperar o estado central do lote;
- erros de autenticação, internet, dispositivo, cota, espaço e integridade deverão ser
  exibidos em linguagem simples e com ação disponível;
- credenciais, refresh token e URL retomável são proibidos no navegador e nos logs.

### 21 de agosto de 2026 — versão 0.33

- corrigido o ciclo de vida das tarefas do `QThreadPool`, mantendo-as até o sinal final;
- registrado o ensaio real em que a empresa foi criada com HTTP `201`, mas a interface
  permaneceu em processamento antes da correção;
- registro da máquina tornou-se automático após selecionar ou criar uma empresa;
- removido do fluxo normal o botão `Conectar máquina`; `Tentar novamente` aparece
  somente quando o registro falha;
- suíte do agente ampliada para 31 testes, com Ruff aprovado;
- instalador `0.1.1` existente não contém as correções mais recentes e não deve ser
  tratado como nova baseline até recompilação autorizada;
- Fase 6 permanece planejada; próxima implementação começa por contratos, adaptador
  local simulado e persistência de uploads antes da integração OAuth real.

### 21 de agosto de 2026 — versão 0.32

- agente passou a criar empresa, cliente e múltiplos projetos pela API central;
- criação da empresa mantém atribuição automática de Proprietário no backend;
- todo projeto continua obrigatoriamente vinculado a um cliente;
- seletores são atualizados imediatamente e projetos são filtrados pelo cliente;
- Ruff, 29 testes do agente e 6 testes de integração backend foram aprovados;
- validação visual e detecção automática de discos permanecem pendentes.

### 19 de agosto de 2026 — versão 0.31

- concluído tecnicamente o último item da Fase 4 com abertura contextual do catálogo;
- iniciada a Fase 5 com React, TypeScript, Vite, OIDC/PKCE e contexto empresarial;
- entregues catálogo, busca, edição de metadados e tags na primeira fatia web;
- frontend integrado ao Docker local e validado por testes, tipos, build e HTTP;
- definida paleta principal verde, branca e preta;
- login real, dados de ensaio e validação visual permanecem pendentes.

### 19 de agosto de 2026 — versão 0.30

- implementado o núcleo da organização local segura da Fase 4;
- destino passa a integrar a prévia e toda movimentação exige confirmação explícita;
- adotados checkpoints SQLite, uma operação ativa e retomada sem repetição;
- movimentação no mesmo volume não substitui; entre volumes copia em streaming,
  verifica SHA-256 e somente depois remove a origem;
- adotado identificador de ingestão local único para o catálogo central;
- caminhos de origem e destino permanecem exclusivamente no agente;
- abertura do frontend e validação funcional no Windows permanecem pendentes.

### 19 de agosto de 2026 — versão 0.29

- criada continuidade operacional única para retomada do MVP;
- consolidados estados das Fases 0 a 8 e evidências de backend e agente;
- registrado que alterações ainda não commitadas pertencem ao estado atual;
- corrigidos índices e referências que ainda apontavam para o início do backend;
- Fases 2 e 3 permanecem aguardando validação funcional no ambiente oficial;
- Fase 4 confirmada como próxima arquitetura e implementação, sujeita a aprovação.

### 19 de agosto de 2026 — versão 0.28

- implementada análise local somente leitura com SHA-256 em streaming;
- caminhos completos e prévias permanecem exclusivamente no SQLite do agente;
- itens técnicos, temporários, links e junções são excluídos da varredura;
- duplicidades por conteúdo e conflitos de destino são apresentados ao usuário;
- prévia e seleção sobrevivem ao reinício, e cancelamento preserva itens concluídos;
- movimentação física permanece proibida até a implementação confirmada da Fase 4.

### 19 de agosto de 2026 — versão 0.27

- implementado o agente local mínimo em Python/PySide6 com camadas separadas;
- adotados SQLite migrável, instalação persistente e fila idempotente local;
- implementados OIDC/PKCE no navegador, token em memória e novo login após encerramento;
- polling passou a renovar presença e reportar confirmação, execução e resultado;
- declarado realm Keycloak local com cliente público PKCE e audiência da API;
- validação ponta a ponta real mantida pendente até preparar o ambiente local com Python 3.14.

### 1º de agosto de 2026 — versão 0.26

- iniciada a implementação do catálogo audiovisual;
- arquivo lógico separado de versão física e objeto de armazenamento;
- criação e listagem isoladas por empresa e projeto;
- caminho local completo removido antes da persistência central;
- alteração inicial de metadados protegida por concorrência otimista;
- contrato OpenAPI e testes correspondentes adicionados.

### 1º de agosto de 2026 — versão 0.25

- concluída a consolidação dos adaptadores HTTP administrativos;
- criação e listagem de clientes e projetos migradas para casos de uso e portas;
- contexto empresarial, membros e consulta de auditoria retirados do ORM nas views;
- auditoria protegida contra `UPDATE` e `DELETE` diretamente no PostgreSQL;
- tentativas e resultados de e-mail persistidos com destinatário protegido por HMAC;
- fluxo Django, Redis, Celery e Mailpit validado funcionalmente;
- definido `D:\PROJETOS\LEGADO` como caminho definitivo do projeto.

### 1º de agosto de 2026 — versão 0.24

- criação e listagem de convites migradas para casos de uso e portas;
- proteção de dados pessoais e entrega assíncrona isoladas por adaptadores;
- criação, substituição do convite anterior, auditoria e agendamento executados sob unidade de trabalho;
- removidos ORM, criptografia, token e Celery da view de coleção;
- criado teste arquitetural específico para as views de convites.

### 1º de agosto de 2026 — versão 0.23

- tabela `audit_events` evoluída sem criação de fonte concorrente de auditoria;
- adicionados nome e descrição funcional da ação;
- `before` e `after` renomeados para `old_state` e `new_state` com preservação dos dados;
- adicionado `change_state` calculado campo a campo;
- migration preenche os novos campos também para eventos existentes;
- API e testes atualizados para o novo contrato.

### 1º de agosto de 2026 — versão 0.22

- cancelamento de convite migrado para caso de uso e porta de persistência;
- cancelamento e auditoria executados na mesma unidade de trabalho;
- removidos ORM e auditoria direta da view de detalhe do convite;
- adicionado teste de rejeição do aceite após cancelamento.

### 1º de agosto de 2026 — versão 0.21

- aceite de convite migrado para caso de uso independente de framework;
- busca bloqueada do convite, validações, ativação do vínculo e auditoria mantidas na mesma transação;
- removidos ORM, transação e regras de negócio da view de aceite;
- mantidos os erros públicos já definidos no contrato.

### 1º de agosto de 2026 — versão 0.20

- concessão e revogação de acesso a projetos migradas para casos de uso e portas;
- autorização empresarial implementada por adaptador de composição entre módulos;
- persistência e auditoria da alteração de acesso protegidas por unidade de trabalho;
- removidas regras de acesso e imports de ORM da view correspondente.

### 1º de agosto de 2026 — versão 0.19

- iniciada a consolidação das operações administrativas em casos de uso e portas;
- atualização de membros migrada para aplicação independente do framework;
- conflitos de versão padronizados como HTTP `409`;
- criado teste arquitetural contra dependências de framework no domínio e aplicação;
- disponibilizada consulta de auditoria exclusiva para Proprietários.

### 1º de agosto de 2026 — versão 0.18

- implementada auditoria imutável para operações administrativas;
- implementado envio assíncrono de convites por Celery e adaptador de e-mail Django;
- mantidos tokens fora dos eventos de auditoria;
- parametrizados endereço público de aceite e remetente de e-mail.

### 1º de agosto de 2026 — versão 0.17

- implementados convites de uso único com validade de sete dias;
- tokens de convite persistidos somente como resumo SHA-256;
- aceite vinculado ao HMAC do e-mail da conta autenticada;
- implementadas gestão de membros e proteção do último Proprietário ativo;
- implementadas concessão e revogação de acesso a projetos.

### 1º de agosto de 2026 — versão 0.16

- implementada a primeira fatia de clientes e projetos;
- adotado `X-Company-ID` como contexto empresarial explícito da API inicial;
- aplicadas unicidade normalizada e filtragem obrigatória por empresa;
- Administradores recebem acesso automático aos projetos que criarem.

### 1º de agosto de 2026 — versão 0.15

- autorizado o início da implementação incremental;
- confirmado o uso de Daphne como servidor ASGI;
- determinado o uso de containers Docker para os ambientes necessários;
- implementada e validada a base Docker com Django, PostgreSQL e Redis;
- comprovada a persistência dos dados após recriação do container PostgreSQL;
- Git e GitHub permanecem sob responsabilidade exclusiva do proprietário.

### 1º de agosto de 2026 — versão 0.14

- aprovado que dados PostgreSQL permaneçam fora do ciclo de vida dos containers;
- definidos volumes persistentes estáveis e validação obrigatória antes da implantação;
- proibida a criação silenciosa de banco vazio em ambientes persistentes;
- aprovada a esteira de atualização com backup, migration única e verificações de saúde;
- aprovado o padrão de migrations `expandir → migrar → contrair`;
- separadas reversão da aplicação e recuperação dos dados;
- aprovada a política inicial de backup, restauração testada, RPO e RTO do piloto;
- planejados backup físico, WAL/PITR e réplica para a produção comercial;
- implementação do software permanece não autorizada.

### 31 de julho de 2026 — versão 0.13

- documentação fragmentada por categorias, com índice central e monólito v0.12 preservado;
- aprovado o monorepo para backend, agente, frontend, contratos, automações e infraestrutura;
- aprovado o backend como monólito modular Django;
- definidos os módulos iniciais do backend, agente e frontend;
- aprovadas as regras de dependência entre domínio, aplicação, adaptadores e infraestrutura;
- proibidos acesso direto ao ORM de outro módulo e compartilhamento de modelos de persistência;
- definida como próxima etapa a arquitetura de infraestrutura, ambientes e observabilidade;
- criação do esqueleto e implementação do software permanecem não autorizadas.

### 31 de julho de 2026 — versão 0.12

- aprovados os contratos REST e OpenAPI 3.1;
- definidos namespaces públicos, internos, de agente e webhooks;
- aprovados padrões de idempotência, concorrência e operações assíncronas;
- padronizados erros com `application/problem+json` e códigos estáveis;
- iniciada a discussão da estrutura do repositório e módulos;
- implementação permanece não autorizada.

### 31 de julho de 2026 — versão 0.11

- aprovado o modelo conceitual PostgreSQL;
- definidos isolamento multiempresa, RLS, UUIDs e controle de versão;
- separados arquivo lógico, versões físicas e objetos do Drive;
- definidas tabelas conceituais de domínio, integração, notificações e auditoria;
- iniciada a discussão dos contratos de API e tratamento de erros;
- implementação permanece não autorizada.

### 31 de julho de 2026 — versão 0.10

- aprovadas as fontes de verdade central, local e externa;
- aprovados os padrões outbox, inbox e entrega idempotente;
- definidas regras de concorrência, concessão de tarefas e checkpoints;
- definidas as filas Celery e os critérios de confiabilidade;
- iniciada a discussão do modelo de dados PostgreSQL;
- implementação permanece não autorizada.

### 31 de julho de 2026 — versão 0.9

- aprovadas as responsabilidades permitidas e proibidas do n8n;
- definidos os workflows iniciais e os contratos de integração com Django;
- mantido o n8n fora das decisões e transações do domínio;
- iniciada a discussão de filas, retomada, concorrência e idempotência;
- implementação permanece não autorizada.

### 31 de julho de 2026 — versão 0.8

- registrada a disponibilidade de um Drive pessoal pago para testes de integração;
- limitada a integração a uma pasta isolada e a arquivos criados pela aplicação;
- mantida como pendente a validação específica em Drive Compartilhado;
- confirmado o uso interno do n8n Community sem licença paga nesta fase;
- substituído MinIO obrigatório por adaptador local de sistema de arquivos, com S3 compatível opcional;
- implementação permanece não autorizada.

### 31 de julho de 2026 — versão 0.7

- definido uso inicial por uma única produtora e comercialização futura;
- determinado que o desenvolvimento não dependerá de serviços ou licenças pagas;
- limitado o n8n Community ao uso interno inicial;
- definidos adaptadores substituíveis para n8n e Google Drive;
- estabelecida revisão obrigatória de licenças antes da primeira produtora externa;
- implementação permanece não autorizada.

### 31 de julho de 2026 — versão 0.6

- aprovados Google Workspace e Drive Compartilhado como armazenamento principal;
- aprovado o escopo OAuth `drive.file`;
- limitado o gerenciamento aos arquivos enviados pela aplicação;
- definido `NAO_SUPORTADO_PELO_DRIVE` para arquivos acima de 5 TB;
- aprovado o fluxo retomável direto entre agente e Drive;
- iniciada a discussão das responsabilidades e contratos do n8n;
- implementação permanece não autorizada.

### 31 de julho de 2026 — versão 0.5

- aprovada a autenticação do frontend e agente por Keycloak, OpenID Connect e PKCE;
- aprovada a exigência de navegador externo para login do agente;
- aprovada a comunicação de saída por HTTPS e WebSocket seguro;
- definidos comandos persistentes, confirmações e idempotência;
- iniciada a discussão da integração OAuth e do upload retomável do Drive;
- implementação permanece não autorizada.

### 31 de julho de 2026 — versão 0.4

- adotados Clean Architecture, Clean Code e princípios SOLID em todo o projeto;
- definida a separação entre domínio, aplicação, adaptadores e infraestrutura;
- estabelecida a regra de uma classe por arquivo, com exceção de código gerado, migrations e configuração declarativa;
- implementação permanece não autorizada.

### 31 de julho de 2026 — versão 0.3

- aprovada a stack Python para backend e agente local;
- selecionados Django, Django REST Framework, PostgreSQL, Redis, Celery, Channels e Keycloak para o backend;
- selecionados Python, PySide6 e SQLite para o agente local;
- mantidos React, TypeScript e Vite no frontend;
- iniciada a arquitetura de autenticação e comunicação agente–backend;
- definido que o agente exigirá nova autenticação após todo reinício do computador;
- implementação permanece não autorizada.

### 31 de julho de 2026 — versão 0.2

- concluídas e aprovadas as regras de negócio pendentes da seção 37;
- detalhadas regras de empresa, usuários, projetos, catálogo, upload, notificações, downloads e conformidade;
- iniciada a fase de comparação e seleção de tecnologias;
- implementação permanece não autorizada.

### 31 de julho de 2026 — versão 0.1

- criado o documento mestre único;
- consolidadas as decisões das conversas de descoberta;
- registrada a arquitetura funcional híbrida;
- registradas regras de empresas, usuários, organização, upload, catálogo, Drive, download, lixeira, logs e alertas;
- registradas as pendências para a próxima conversa;
- implementação permanece não autorizada.

