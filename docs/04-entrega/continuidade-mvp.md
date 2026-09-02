# Continuidade do MVP

**Produto:** Gerenciador de Áudio Visual.

**Atualizado em:** 31 de agosto de 2026.

Documento operacional para qualquer pessoa ou IA retomar o projeto sem depender do
histórico de conversas. Regras de negócio e decisões arquiteturais continuam nos
documentos temáticos; este arquivo indica o estado concreto e o próximo ponto de
trabalho.

## Local e fontes de verdade

- projeto oficial: `D:\PROJETOS\LEGADO`;
- não utilizar referências antigas a `E:\Projetos`;
- execução do MVP: [Roadmap do MVP](roadmap-mvp.md);
- itens objetivos: [Checklist do MVP](checklist-mvp.md);
- inventário técnico: [Estado da implementação](estado-implementacao.md);
- evidências: [Plano de testes](plano-testes.md);
- decisões vigentes: [Registro de decisões](../decisoes/registro-decisoes.md).

O worktree contém alterações ainda não commitadas das fases implementadas. Elas fazem
parte do projeto atual. Não executar `git reset`, descarte, limpeza ou sobrescrita para
retornar ao último commit.

## Estado resumido

| Fase | Estado | Evidência principal |
|---|---|---|
| 0 — estabilização | VALIDADO | Docker, migrations, saúde, Ruff e baseline aprovados |
| 1 — catálogo | VALIDADO | catálogo, tags, histórico, filtros, reconciliação e 55 testes backend |
| 2 — agente mínimo | IMPLEMENTADO — AGUARDA VALIDAÇÃO | SQLite, OIDC/PKCE, heartbeat, comandos e fila |
| 3 — análise e prévia | IMPLEMENTADO — AGUARDA VALIDAÇÃO | análise somente leitura, SHA-256, conflitos, prévia e 17 testes agente |
| 4 — organização segura | IMPLEMENTADO — AGUARDA VALIDAÇÃO | movimentação, checkpoints, catálogo e abertura contextual implementados; falta ensaio funcional |
| 5 — frontend web | EM IMPLEMENTAÇÃO | primeira fatia Docker com autenticação, contexto, catálogo, edição e tags |
| 6 — Drive | IMPLEMENTADO — AGUARDA ENSAIOS DE FALHA | OAuth, árvore, lotes, envio real, confirmação e painel validados |
| 7 — tempo real | IMPLEMENTADO — AGUARDA ENSAIO | WebSocket seguro, polling e reconciliação cobertos |
| 8 — fechamento | EM IMPLEMENTAÇÃO | testes automatizados e rotinas de backup prontas; faltam ensaio e release externa |

## Software disponível

### Backend

- identidade OIDC e projeção local de usuário;
- empresas, convites, membros e papéis;
- clientes, projetos e acessos;
- auditoria imutável e notificações por e-mail;
- catálogo, versões físicas, tags, histórico e filtros;
- máquinas, presença, comandos persistidos e reconciliação;
- contrato OpenAPI 3.1 e infraestrutura Docker local.

### Agente local

- Python 3.14 como requisito oficial e PySide6;
- UUID persistente da instalação e SQLite migrável;
- token OIDC somente em memória;
- heartbeat, polling e ciclo de comandos;
- seleção autenticada de empresa, cliente e projeto;
- criação de empresa, cliente e múltiplos projetos pelos fluxos oficiais da API;
- identificação técnica automática da instalação após login e seleção da empresa;
- nenhuma conexão, aprovação ou repetição manual de máquina; falhas transitórias são
  repetidas automaticamente;
- tarefas HTTP retidas até a entrega do resultado à interface Qt;
- seleção de arquivos, pastas e HARD DISK;
- exclusão de itens técnicos, temporários, links e junções;
- metadados básicos e data do sistema de arquivos;
- SHA-256 em streaming de 4 MiB;
- duplicidades e conflitos de destino;
- prévia selecionável, cancelável e recuperável após reinício;
- tela de destino aberta em cada análise, com escolha entre mídia e pasta no PC;
- resolução explícita de conflitos e duplicidades;
- movimentação sem sobrescrita, com verificação SHA-256 entre volumes;
- checkpoint por arquivo, interrupção e retomada sem mover novamente;
- ingestão idempotente no catálogo sem transmitir caminhos locais.
- último destino persistido no SQLite v5 somente como sugestão;
- destino `Cliente/Projeto/Ano/Mês/Dia` calculado e exibido na prévia;
- destinos dentro da origem selecionada são bloqueados para evitar recursão.

## Validações registradas

### Backend — última baseline

- 66 testes aprovados;
- Ruff aprovado;
- migrations aplicadas e sem mudanças pendentes;
- OpenAPI 3.1 válido, com avisos documentais não bloqueadores;
- migrations `drive.0002`, `drive.0003` e `uploads.0001` aplicadas no PostgreSQL local;
- PostgreSQL, Redis, backend, Celery e Mailpit validados;
- saúde `live` e `ready` aprovada.

### Agente — última baseline

- 41 testes aprovados;
- Ruff aprovado;
- SQLite v1→v4 validado sem perder o identificador da instalação;
- conteúdo e horário dos arquivos de origem preservados;
- cancelamento e recuperação da prévia validados;
- limites arquiteturais validados;
- testes executados no runtime auxiliar Python 3.12.
- 6 testes backend das coleções de empresas, clientes e projetos aprovados.
- login OIDC e criação real de empresa chegaram ao backend com HTTP `201`;
- o ensaio revelou perda do retorno assíncrono na interface; a tarefa passou a ser
  retida até o sinal final e a regressão foi coberta automaticamente;
- o instalador `0.1.1` existente antecede as correções assíncronas e de conexão
  automática; usar o código-fonte até uma recompilação explicitamente autorizada.

### Frontend — primeira baseline

- 21 testes aprovados;
- checagem TypeScript e build Vite aprovados;
- imagem Docker construída e composição validada;
- frontend e proxy do backend responderam HTTP `200`;
- paleta principal verde, branca e preta aplicada.

### Google Drive — OAuth

- backend e frontend implementados para conectar, consultar e desconectar uma conta por empresa;
- OAuth, autorização e árvore idempotente cobertos por 4 testes do módulo Drive;
- build TypeScript/Vite, `manage.py check` e consistência de migrations aprovados;
- credenciais OAuth configuradas localmente e reconhecidas pelo Google;
- autorização real concluída com uma conta de teste pelo frontend;
- URI de retorno exigida: `http://127.0.0.1:8000/api/v1/drive/oauth/callback`.
- árvore diária implementada em `Gerenciador de Áudio Visual/Empresa/Projeto/AAAA.MM/DD`,
  com `Originais`, `Previews` e `Entregas` e IDs persistidos no PostgreSQL.
- ensaio real aprovado em 26 de agosto de 2026: oito pastas confirmadas diretamente
  pela API do Drive e segunda execução sem duplicação.

### Google Drive — lotes e transporte retomável

- lotes, itens, tentativas e checkpoints persistidos no PostgreSQL;
- conta e pastas de destino vinculadas imutavelmente ao lote;
- sessão temporária cifrada e entregue somente ao agente responsável;
- envio direto em blocos implementado sem passagem do binário pelo backend;
- checkpoints persistidos no SQLite v4 e no PostgreSQL após confirmação do Drive;
- sessão expirada renovada em nova tentativa;
- 41 testes do agente, 66 testes backend e 21 testes frontend aprovados;
- ensaio real aprovado em 29 de agosto de 2026 com arquivo de 17 MiB, interrupção após
  8 MiB, consulta da sessão, retomada no byte confirmado e conclusão `200`;
- objeto `1AKCnXgcDJTU-776goINqlcwinGql4Aor` confirmado na pasta `Originais`, com
  tamanho e SHA-256 idênticos aos dados locais;
- DNS externo do backend Docker voltou a resolver os endpoints OAuth e Drive após a
  reativação e recriação dos containers, sem necessidade de DNS fixo na composição.

### Frontend — painel de lotes

- criação por projeto, data, categoria e arquivos catalogados;
- máquina de origem determinada pela versão física, sem misturar máquinas no lote;
- chave de idempotência preservada durante repetição da mesma tentativa;
- progresso geral e individual calculado por bytes confirmados pelo Drive;
- lote ativo recuperado após recarga e atualizado por polling até estado final;
- falhas de conexão, Drive e conflito apresentadas em linguagem simples;
- pausa, retomada e cancelamento solicitados pela interface e aplicados pelo agente
  antes do próximo bloco seguro;
- lote pausado permanece estável até retomada explícita e o progresso não regride;
- internet, autenticação, cota, disco e integridade possuem mensagens operacionais simples;
- tokens CSS centralizam paleta, estados, superfícies, sombras, raios e dimensões.

### Tempo real e reconciliação

- WebSocket avisa mudanças de lote e invalida os dados mantidos pelo frontend;
- polling continua ativo como contingência e fonte periódica de reconciliação;
- ingresso do canal expira em 60 segundos, é usado uma única vez e não contém token OIDC;
- associação bloqueada é rejeitada na conexão e encerra canal já aberto no próximo evento;
- checkpoint confirmado pelo Drive atualiza PostgreSQL e corrige o SQLite antes do próximo bloco.

### Validação operacional mais recente

- Docker Desktop reativado em 29 de agosto de 2026;
- PostgreSQL, Redis, backend, três processos Celery, frontend, Keycloak e Mailpit ativos;
- backend e frontend recriados a partir da composição vigente;
- interface, `health/live`, `health/ready`, descoberta OIDC e Mailpit responderam
  HTTP `200`;
- transporte retomável no Google Drive real aprovado após a validação operacional.

## Validações ainda pendentes

- executar o agente no Python 3.14 oficial;
- revalidar o login OIDC do agente após a troca de marca;
- validar sessão autenticada e processamento de tarefa ponta a ponta;
- ensaiar seleção, recuperação e progresso pela interface visível;
- validar a extração avançada da data original de câmera quando houver adaptador.
- ensaiar organização real em mesmo volume, entre volumes e após desconexão;
- validar login, seleção contextual, catálogo, edição e tags com dados reais;
- validar visualmente responsividade e acessibilidade do frontend.

## Próxima implementação

Preservar o fluxo validado e concluir a Fase 8:

1. revalidar pela interface o login e a sessão automática, sem ação específica da máquina;
2. executar E2E visual completo no Windows, inclusive queda do WebSocket;
3. ensaiar cota, falta de espaço e expiração de autenticação com serviços reais;
4. ensaiar backup e restauração com os serviços parados;
5. implementar detecção automática de discos externos no agente;
6. validar o fluxo completo no Python 3.14 oficial;
7. recompilar o instalador somente após nova autorização e validação do código-fonte;
8. publicar tag e release somente após autorização explícita.

O frontend da Fase 6 é obrigatório para o aceite do MVP. Ele usa WebSocket como aviso
e polling automático como contingência. Refresh token, credenciais
OAuth e URL retomável nunca serão entregues ao navegador.

## Critérios obrigatórios da Fase 4

- nenhum arquivo pode ser apagado ou sobrescrito;
- a origem não pode ser alterada antes da confirmação;
- uma repetição não pode refazer movimentação concluída;
- conflitos não podem ser resolvidos silenciosamente;
- checkpoints locais não podem conter tokens ou credenciais;
- desconexão deve interromper novas movimentações;
- testes devem usar arquivos temporários e verificar conteúdo e destino;
- roadmap, checklist, estado e testes devem ser atualizados com o diff explicado.

## Ordem de leitura para retomada

1. este documento;
2. [Roadmap do MVP](roadmap-mvp.md);
3. [Checklist do MVP](checklist-mvp.md);
4. [Organização local](../02-regras-negocio/organizacao-local.md);
5. [Filas, retomada e idempotência](../03-arquitetura/filas-retomada-idempotencia.md);
6. código e testes existentes em `agent/`;
7. continuar a Fase 8 pelos ensaios E2E, backup e restauração.
