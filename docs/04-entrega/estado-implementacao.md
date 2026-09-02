# Estado da implementação

**Produto:** Gerenciador de Áudio Visual.

> Execução vigente: [Roadmap do MVP funcional](roadmap-mvp.md) e [Checklist do MVP](checklist-mvp.md).
> Retomada operacional: [Continuidade do MVP](continuidade-mvp.md).

**Estado:** EM IMPLEMENTAÇÃO desde 1º de agosto de 2026.

**Última consolidação:** 31 de agosto de 2026. Fases 0 e 1 validadas; Fases 2 e
3 implementadas e aguardando validação funcional; Fase 4 tecnicamente concluída e
aguardando ensaio funcional; Fase 5 executável e OAuth, árvore, lotes, sessão retomável,
envio real em blocos e painel de lotes da Fase 6 implementados; Fase 7 implementada
com WebSocket seguro, polling de contingência e reconciliação retomável.

Registro operacional do software implementado, das validações executadas, das limitações conhecidas e do ponto obrigatório de continuidade.

> As decisões arquiteturais e regras de negócio permanecem nos documentos temáticos. Este arquivo registra somente o estado concreto da implementação.

## Base executável

### Backend

- projeto Python 3.14 com Django, Django REST Framework e Daphne;
- PostgreSQL como persistência central;
- Redis para cache, canais e filas;
- Celery Worker, fila crítica e Celery Beat previstos na composição local;
- autenticação OIDC com Keycloak e projeção local de usuário;
- endpoints de saúde e erros `application/problem+json`;
- configurações sensíveis fornecidas por ambiente;
- execução dos componentes de servidor em Docker.

### Agente local

**Estado:** IMPLEMENTADO — AGUARDA VALIDAÇÃO FUNCIONAL.

- projeto Python 3.14 e PySide6 separado em domínio, aplicação, adaptadores e infraestrutura;
- instalação identificada tecnicamente por UUID persistente, sem aprovação de máquina;
- SQLite migrável com fila idempotente e sem senha, token ou credencial;
- login OIDC Authorization Code com PKCE S256 no navegador e retorno em `localhost`;
- token mantido somente na memória do processo e descartado no encerramento;
- heartbeat renovado a cada consulta, polling incremental e retomada da fila local;
- confirmação, execução, resultado de `PING` e falha explícita de comando não suportado;
- interface inicial para login, empresa, presença e acompanhamento da fila;
- criação guiada de empresa, cliente e múltiplos projetos pela API central;
- projetos filtrados pelo cliente selecionado e contexto atualizado sem reiniciar;
- tarefas HTTP mantidas vivas até o retorno à interface, evitando estado visual preso;
- identificação técnica iniciada silenciosamente após login e seleção da empresa;
- falhas transitórias da sessão são repetidas automaticamente, sem ação do usuário;
- realm local declarativo com clientes `legado-agent`, `legado-web` e `legado-api`.
- ação de autenticação identificada como `LOGIN`;
- botão `Selecionar HD` inclui uma mídia inteira nas origens da análise;
- cada análise abre a escolha de mídia ou pasta no PC para o destino;
- último destino persiste em `agent_settings` no SQLite v5 somente como sugestão;
- subpastas de cliente, projeto e data são calculadas automaticamente e mostradas na prévia;
- destino dentro da origem selecionada é bloqueado para impedir processamento recursivo.

### Upload direto no agente

**Estado:** IMPLEMENTADO E VALIDADO NO DRIVE REAL — AGUARDA ENSAIOS DE FALHA.

- comando `UPLOAD_FILE` referencia somente o item central;
- backend devolve sessão, versão lógica, tamanho e checksum após validar a máquina;
- caminho local é resolvido pelo `media_file_id` exclusivamente no SQLite;
- tamanho e SHA-256 são verificados antes do envio;
- blocos padrão de 8 MiB respeitam o múltiplo de 256 KiB;
- respostas `308` avançam somente pelo byte confirmado pelo Drive;
- respostas `404/410` renovam a sessão em nova tentativa;
- respostas `200/201` concluem o transporte;
- SQLite v4 persiste trabalho, tentativa, progresso e falha resumida;
- URL retomável permanece apenas em memória;
- falha de rede deixa o trabalho `INTERRUPTED` e retomável;
- resultado do comando contém somente item e bytes confirmados.
- ID final devolvido pelo Drive é confirmado pelo backend antes da conclusão;
- objeto físico persiste conta, pasta, nome, tamanho, checksum e tipo MIME;
- catálogo muda para `SINCRONIZADO` somente após validação central idempotente;

### Análise e prévia local

**Estado:** IMPLEMENTADO — AGUARDA VALIDAÇÃO FUNCIONAL.

- seleção acumulável de arquivos, pastas e HARD DISK pela interface;
- varredura somente leitura sem seguir links ou junções;
- lixeira, diretórios técnicos, arquivos temporários e itens do sistema ignorados;
- nome, extensão, tipo MIME, tamanho, data e origem da data registrados localmente;
- SHA-256 calculado em blocos de 4 MiB, sem carregar o arquivo inteiro em memória;
- alteração de tamanho ou horário durante a leitura invalida o item;
- duplicidade por checksum e conflito pelo destino relativo detectados;
- destino previsto em `Cliente/Projeto/Ano/Mês/Dia`, com segmentos seguros para Windows;
- prévia selecionável persistida e recuperável após reinício;
- cancelamento entre arquivos preserva a prévia parcial;
- a análise permanece somente leitura; a movimentação foi isolada no fluxo de
  organização segura, sempre após confirmação.

### Persistência e desenvolvimento

- volume PostgreSQL externo e estável;
- bloqueio da criação silenciosa de banco vazio;
- serviço separado para migrations;
- Ruff, pytest e verificação de migrations disponíveis no container de desenvolvimento;
- dados reais, segredos e volumes excluídos do repositório.

### Frontend web

**Estado:** EM IMPLEMENTAÇÃO — PRIMEIRA FATIA EXECUTÁVEL.

- React 19, TypeScript, Vite, React Router e TanStack Query;
- login obrigatório Keycloak OIDC/PKCE, com token somente em memória;
- seleção de empresa e projeto e rota contextual do catálogo;
- listagem, busca, resumo, edição de metadados e aplicação ou remoção de tags;
- cliente HTTP com token e empresa somente em cabeçalhos;
- painel Google Drive com conexão, estado e desconexão por empresa;
- troca da conta restrita ao papel Proprietário e mensagens operacionais simples;

### Google Drive — OAuth

**Estado:** IMPLEMENTADO E VALIDADO COM CONTA GOOGLE REAL.

- Authorization Code processado exclusivamente pelo backend;
- escopo mínimo `drive.file`, além de `openid email` para identificar a conta;
- estado aleatório com validade de dez minutos, hash persistido e consumo único;
- refresh token e e-mail criptografados no PostgreSQL;
- token, segredo do cliente e código de autorização não são enviados ao frontend;
- conexão isolada por empresa e gerenciamento exclusivo do Proprietário;
- desconexão remove imediatamente a credencial e os dados locais da conta;
- árvore idempotente `Empresa/Projeto/AAAA.MM/DD` com destinos `Originais`, `Previews`
  e `Entregas`, IDs e pais persistidos;
- callback retorna somente `connected` ou `error` ao frontend;
- variáveis de ambiente e contrato OpenAPI adicionados sem segredos reais.
- credenciais carregadas pelo ambiente sem exposição em logs ou respostas;
- endpoint do Google reconheceu o cliente OAuth configurado;
- autorização real concluída e conta Google conectada pelo frontend;
- tipos principais gerados do contrato OpenAPI;
- estados de carregamento, vazio, erro e layout responsivo para pessoa não técnica;
- paleta visual principal verde, branca e preta;
- execução local e por serviço Docker `web`.

## Módulos implementados

### Identidade

**Estado:** IMPLEMENTAÇÃO INICIAL VALIDADA.

- validação de token OIDC;
- sincronização da projeção do usuário autenticado;
- e-mail criptografado e índice exato protegido por HMAC;
- endpoint do usuário autenticado.

### Empresas

**Estado:** IMPLEMENTAÇÃO INICIAL VALIDADA.

- criação e listagem de empresas;
- criação automática do vínculo de Proprietário;
- vínculos com papéis `OWNER` e `ADMINISTRATOR`;
- estados `ACTIVE`, `BLOCKED` e `LEFT`;
- convites de uso único com validade de sete dias;
- token de convite persistido somente como resumo SHA-256;
- e-mail do convite criptografado e associado por HMAC;
- aceite restrito à conta autenticada correspondente;
- aceite separado em caso de uso, DTOs, porta e adaptador de persistência;
- aceite, ativação do vínculo e auditoria protegidos pela mesma transação;
- cancelamento e substituição de convite pendente;
- cancelamento separado em caso de uso, porta e adaptador de persistência;
- cancelamento e auditoria protegidos pela mesma transação;
- criação e listagem separadas em casos de uso, portas e adaptadores;
- criação, substituição anterior, auditoria e agendamento protegidos por unidade de trabalho;
- listagem e alteração de membros por Proprietários;
- proteção do último Proprietário ativo;
- concorrência otimista na alteração de membro por `expected_version`;
- conflito de versão retornado como HTTP `409`.

### Clientes e projetos

**Estado:** IMPLEMENTAÇÃO INICIAL VALIDADA.

- criação e listagem de clientes e projetos;
- nome original e normalizado;
- unicidade de cliente por empresa e de projeto por cliente;
- contexto empresarial explícito por `X-Company-ID`;
- isolamento inicial entre empresas;
- acesso automático do Administrador ao projeto criado por ele;
- concessão e revogação de acesso por Proprietários.
- criação e listagem isoladas em casos de uso, DTOs, portas e adaptadores de persistência;
- views administrativas sem acesso direto ao ORM ou transações.

### Auditoria

**Estado:** IMPLEMENTAÇÃO INICIAL VALIDADA.

- eventos funcionais para convites, membros e acessos de projeto;
- estado anterior e posterior quando aplicável;
- nome legível e descrição funcional da ação;
- `old_state`, `new_state` e `change_state` persistidos por evento;
- `change_state` calculado automaticamente somente com campos alterados;
- empresa, ator, objeto, correlação e data registrados;
- consulta limitada aos Proprietários da empresa;
- alteração e exclusão por instância bloqueadas no modelo;
- tokens e segredos ausentes dos eventos.

### Notificações

**Estado:** IMPLEMENTAÇÃO INICIAL VALIDADA.

- envio de convite enfileirado por Celery;
- adaptador de e-mail baseado no Django;
- endereço público de aceite e remetente configuráveis;
- política de repetição com atraso progressivo;
- composição do e-mail validada com backend de teste em memória.
- tentativas e resultados persistidos sem endereço aberto, token ou mensagem sensível;
- estados de processamento, entrega e falha com número da tentativa e tarefa Celery;
- fluxo real Django, Redis, Celery e Mailpit validado.

### Catálogo audiovisual

**Estado:** IMPLEMENTAÇÃO INICIAL PARCIAL VALIDADA.

- arquivo lógico separado da primeira versão física e do objeto de armazenamento;
- criação e listagem por casos de uso, portas e adaptadores;
- tamanho e checksum persistidos na versão física;
- caminho local completo removido antes da persistência central;
- isolamento por empresa e acesso por projeto;
- Proprietários visualizam todos os projetos e Administradores somente os atribuídos;
- alteração inicial de metadados com concorrência otimista e conflito HTTP `409`;
- histórico imutável de snapshots funcionais a cada versão de metadados;
- tags genéricas pré-cadastradas e tags personalizadas isoladas por empresa;
- criação e arquivamento de tags personalizadas restritos a Proprietários;
- aplicação e remoção de tags limitadas aos projetos acessíveis;
- busca textual e filtros por projeto, estado e tag;
- paginação por cursor opaco, sem uso de deslocamento;
- contrato inicial de criação, listagem e alteração disponível no OpenAPI.
- estados técnicos oficiais e transições permitidas centralizados na aplicação;
- reconciliação autenticada por empresa, usuário, máquina e projeto;
- primeira máquina reconciliadora vinculada à versão física;
- repetição do mesmo estado idempotente, sem nova versão ou auditoria;
- transição com versão desatualizada rejeitada com HTTP `409`;
- transição inválida rejeitada sem alterar o catálogo;
- mudanças de estado registradas em auditoria imutável.
- aplicação e remoção de tags idempotentes e auditadas;
- tags incluídas nas respostas de criação, listagem, edição e reconciliação;
- histórico de metadados paginado e isolado por empresa e projeto;
- restauração de metadados como nova versão, restrita a Proprietários;
- restauração concorrente protegida por `expected_version`;
- filtros combináveis por extensão, tipo, tamanho, período e responsável.

## Contratos disponíveis

- conexão, consulta e desconexão da conta Google Drive;
- criação ou reutilização da árvore diária em `/api/v1/drive/folders/ensure`;
- saúde do processo e prontidão;
- usuário autenticado;
- empresas;
- clientes e projetos;
- convites e aceite;
- membros;
- concessão e revogação de acesso a projetos;
- consulta de auditoria.
- heartbeat autenticado de máquinas;
- criação idempotente e consulta persistida de comandos do agente.
- confirmação, progresso e resultado com versão otimista e transições sem regressão.
- reconciliação técnica de arquivo pelo agente em `/api/v1/agent/media-files/{media_file_id}/state`.
- histórico em `/api/v1/media-files/{media_file_id}/metadata-history`;
- restauração em `/api/v1/media-files/{media_file_id}/metadata-history/{version}/restore`.

O contrato vigente está em `contracts/openapi/v1.yaml`.

## Migrations existentes

- `identity/0001_initial.py`: projeção de usuários;
- `companies/0001_initial.py`: empresas e vínculos;
- `companies/0002_invitationmodel.py`: convites;
- `projects/0001_initial.py`: clientes, projetos e acessos;
- `audit/0001_initial.py`: eventos funcionais de auditoria;
- `audit/0002_audit_event_details.py`: nome, descrição, estados renomeados e diferenças calculadas.
- `audit/0003_protect_audit_events.py`: bloqueio de `UPDATE` e `DELETE` no PostgreSQL;
- `notifications/0001_initial.py`: tentativas e resultados de entrega.
- `catalog/0001_initial.py`: arquivos lógicos, versões físicas e objetos de armazenamento.
- `catalog/0002_metadataversionmodel.py`: histórico versionado de metadados funcionais.
- `catalog/0003_tags.py`: tags genéricas, personalizadas e vínculos com arquivos.
- `catalog/0004_media_file_status_constraint.py`: estados oficiais e restrição de integridade no PostgreSQL.
- `catalog/0005_fileversion_ingestion_id.py`: ingestão idempotente originada pelo agente.
- `operations/0001_initial.py`: máquinas, presença e comandos persistidos.
- `operations/0002_agent_command_execution.py`: progresso, resultado e marcos de execução.
- `drive/0001_initial.py`: conta OAuth e estado temporário de autorização.
- `drive/0002_drivefoldermodel.py`: IDs e hierarquia idempotente das pastas do Drive.

## Arquitetura aplicada

- monólito modular Django;
- módulos organizados por domínio funcional;
- entidades e objetos de valor sem dependência de framework;
- atualização de membros separada em caso de uso, portas e adaptadores;
- concessão e revogação de acesso a projetos separadas em casos de uso, portas e adaptadores;
- alteração de acesso e respectiva auditoria protegidas pela mesma transação;
- teste arquitetural contra imports de Django, DRF e Celery em `domain` e `application`;
- teste arquitetural contra ORM e transações em todos os adaptadores HTTP;
- uma classe ou unidade principal por arquivo, respeitadas as exceções aprovadas.

## Validações executadas

- baseline reproduzível da Fase 0 validada em 18 de agosto de 2026;
- imagens atuais de backend, workers e Celery Beat reconstruídas;
- PostgreSQL, Redis, backend, workers, Celery Beat e Mailpit operacionais;
- endpoints `/health/live` e `/health/ready` aprovados após a reconstrução;
- 57 testes automatizados do backend aprovados;
- 64 testes automatizados do backend aprovados após os controles operacionais;
- lint Ruff aprovado;
- `makemigrations --check --dry-run` sem mudanças pendentes;
- testes de identidade, criptografia, empresas, projetos, convites e permissões;
- testes de isolamento empresarial e proteção do último Proprietário;
- testes de concorrência, auditoria, cálculo de diferenças, e-mail e limites arquiteturais.
- teste de imutabilidade direta no PostgreSQL;
- validação funcional real de Django, Redis, Celery e Mailpit.
- testes de catálogo, remoção de caminho local, permissões por projeto e concorrência.
- testes de tags, busca, cursor, máquinas, comandos, idempotência e transições de execução;
- testes de estados do catálogo, idempotência, versão, vínculo de máquina e isolamento empresarial;
- testes de auditoria idempotente de tags, histórico paginado, restauração e filtros combinados;
- OpenAPI 3.1 validado sem erros; permanecem avisos documentais não bloqueadores;
- contrato regenerado no frontend, migration `drive.0002` aplicada e build Vite aprovado;
- ensaio real da árvore aprovado em 26 de agosto de 2026: oito pastas confirmadas pela
  API do Google Drive, todas ativas, com um único pai, e segunda execução idempotente
  sem novos registros;
- sessão retomável coberta por teste integrado: URL cifrada, reutilização, vínculo à
  máquina, checkpoint confirmado, expiração e renovação em nova tentativa;
- agente envia blocos alinhados diretamente ao Drive, persiste checkpoints no SQLite
  v4 e recupera sessões expiradas sem armazenar a URL temporária;
- migrations de catálogo e operações aplicadas ao PostgreSQL local.
- 7 testes automatizados do agente aprovados em runtime auxiliar Python 3.12;
- Ruff do agente aprovado;
- tela PySide6 validada em modo sem exibição;
- JSON do realm Keycloak e composição Docker validados estaticamente.
- 31 testes automatizados do agente aprovados após o incremento administrativo e
  a correção do ciclo de vida assíncrono;
- upgrade SQLite v1→v4 validado sem perda da identificação da instalação;
- conteúdo e horário dos arquivos de origem preservados nos testes;
- recuperação da prévia e persistência da seleção validadas;
- limites entre domínio, aplicação e infraestrutura do agente validados automaticamente.
- movimentação segura, cópia verificada, checkpoints e retomada validados com arquivos temporários;
- contrato de ingestão idempotente implementado e Ruff aprovado no backend;
- migration `catalog.0005` aplicada no PostgreSQL local;
- 5 testes do frontend, checagem TypeScript e build Vite aprovados;
- imagem Docker do frontend construída, composição validada e serviço iniciado;
- frontend e proxy de saúde do backend responderam HTTP `200`.
- criação no gateway e na tela do agente validada com múltiplos projetos;
- 6 testes backend específicos de empresas, clientes e projetos aprovados.
- login real do agente e criação real de empresa confirmados no backend com HTTP `201`;
- retenção da tarefa no `QThreadPool`, conexão automática e recuperação após falha
  cobertas nos testes da interface;
- composição local reativada e validada em 29 de agosto de 2026 com PostgreSQL,
  Redis, backend, três processos Celery, frontend, Keycloak e Mailpit operacionais;
- interface, saúde do backend, prontidão, descoberta OIDC e Mailpit responderam
  HTTP `200` após a recriação dos serviços da aplicação.
- ensaio real de 17 MiB retomado no byte confirmado e validado por ID, tamanho e SHA-256;
- painel cria e recupera lotes, apresenta progresso geral/individual e encerra polling
  em estado final; suíte completa do backend totalizou 63 testes;
- CSS consolidado em tokens centrais e build de produção aprovado.
- controles idempotentes de pausa, retomada e cancelamento persistidos e aplicados
  pelo agente antes do próximo bloco;
- falhas normalizadas para internet, autenticação, cota, disco e integridade, mantendo
  checkpoint monotônico e mensagem simples no painel.
- status técnicos de lote, arquivo e tentativa permanecem estáveis nos contratos, mas
  são apresentados em português no painel por um mapeamento visual centralizado;
- 36 testes automatizados do agente, 5 testes do frontend, checagem TypeScript, build
  Vite e 64 testes do backend aprovados no fechamento dos controles operacionais;
- backend e frontend reconstruídos após as migrations e confirmados saudáveis.
- WebSocket implementado como aviso com polling de contingência e reconexão exponencial;
- ingresso efêmero de uso único validado, sem token OIDC na URL;
- bloqueio da associação encerra canal já aberto no próximo evento;
- reconciliação Drive → PostgreSQL → SQLite coberta antes da retomada do próximo bloco;
- 66 testes do backend, 41 testes do agente e 21 testes do frontend aprovados;
- TypeScript, build Vite, contrato OpenAPI gerado e Ruff do escopo alterado aprovados;
- backend e frontend reconstruídos em 31 de agosto e confirmados saudáveis.

## Limitações conhecidas

- notificações internas ainda não foram implementadas;
- Row-Level Security ainda não foi aplicada no PostgreSQL;
- ensaio funcional completo do agente em Python 3.14 permanece pendente;
- existe instalador `0.1.1`, mas ele antecede as correções assíncronas e de conexão
  automática; o código-fonte atual deve ser usado até nova compilação autorizada;
- o runtime oficial Python 3.14 não foi instalado devido a falha MSI `1603`; as
  validações atuais usam o runtime auxiliar Python 3.12;
- extração avançada de data original de câmera ainda não possui adaptador por formato;
- Fases 3 e 4 ainda requerem ensaio manual da interface com Python 3.14;
- fluxo real do frontend e OAuth Google validados com conta de ensaio;
- gestão web de clientes, projetos, acessos, operações e auditoria permanece pendente;
  gestão de máquinas não é requisito funcional;
- aprovações, downloads e ensaio visual completo do painel permanecem pendentes.

## Próxima etapa obrigatória

Revalidar o agente atual e concluir a Fase 8:

1. revalidar o login e a sessão técnica automática, sem conexão específica da máquina;
2. executar o E2E visual no Windows, inclusive desconexão do WebSocket;
3. ensaiar cota, falta de espaço e expiração de autenticação com serviços reais;
4. ensaiar backup e restauração em ambiente parado;
5. implementar detecção automática de discos externos no agente;
6. executar o ensaio completo em Python 3.14 quando o runtime estiver disponível;
7. recompilar o instalador somente após autorização explícita;
8. publicar a release somente após os ensaios e autorização específica.

O detalhamento de retomada, limitações do ambiente e ordem de leitura está consolidado
em [Continuidade do MVP](continuidade-mvp.md).

## Critérios de aceite da próxima etapa

- login real abre no navegador e o reinício exige nova autenticação;
- login inicia a sessão automaticamente e uma tarefa é processada sem duplicação;
- usuário removido ou bloqueado perde acesso em todas as instalações na validação seguinte;
- fila local permanece após reinício sem armazenar token;
- análise local não altera arquivos e calcula checksum em streaming;
- prévia completa pode ser reaberta antes da confirmação;
- organização exige confirmação explícita e nunca sobrescreve um destino;
- cada movimentação concluída possui checkpoint idempotente;
- frontend recupera o estado do lote após recarregar a página;
- painel permite selecionar projeto, data, categoria e arquivos da mesma máquina;
- progresso geral e individual usa bytes confirmados pelo Drive e atualização periódica;
- estilos do frontend usam tokens CSS centralizados para cores, superfícies, sombras,
  raios e dimensões estruturais;
- comandos do frontend respeitam autorização e o próximo bloco seguro;
- nenhum segredo OAuth ou URL retomável aparece no navegador ou nos logs;
- Ruff e suítes afetadas permanecem aprovados.

## Protocolo de atualização

Ao concluir cada incremento:

1. atualizar o estado do módulo afetado;
2. registrar contratos, migrations e configurações adicionados;
3. registrar somente validações efetivamente executadas;
4. mover itens concluídos para a seção correspondente;
5. manter limitações e próxima etapa coerentes com o código;
6. atualizar também o roadmap, o plano de testes e o registro de decisões quando aplicável;
7. não marcar como concluído o que estiver apenas planejado ou parcialmente validado.

Consulte também [Estado e roadmap](roadmap.md), [Plano de testes](plano-testes.md), [Estrutura do repositório](../03-arquitetura/estrutura-repositorio.md) e [Decisões e continuidade](../decisoes/registro-decisoes.md).
