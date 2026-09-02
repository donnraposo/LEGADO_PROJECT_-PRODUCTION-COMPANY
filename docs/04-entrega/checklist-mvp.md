# Checklist do MVP

Este checklist acompanha [Roadmap do MVP funcional](roadmap-mvp.md). Um item somente recebe `[x]` depois de implementado e validado.

## Fase 0 — estabilização

- [x] Docker disponível e serviços essenciais saudáveis;
- [x] migrations aplicadas e nenhuma pendente;
- [x] Ruff aprovado;
- [x] testes de catálogo e operações aprovados;
- [x] suíte completa aprovada;
- [x] OpenAPI válido;
- [x] reconstruir backend e workers com a imagem do código atual;
- [x] verificar saúde depois da reconstrução;
- [x] baseline documentada.
- [x] composição completa revalidada em 29 de agosto de 2026 com interface, API,
  prontidão, OIDC e Mailpit respondendo HTTP `200`.

## Fase 1 — catálogo

- [x] estados técnicos e reconciliação autenticada pelo agente;
- [x] auditoria de tags e estados;
- [x] histórico consultável e restaurável;
- [x] filtros restantes e tags nas respostas;
- [x] contratos e testes aprovados.

## Fase 2 — agente mínimo

- [x] scaffold Python/PySide6;
- [x] instalação identificada e SQLite migrável;
- [x] login OIDC/PKCE implementado e autenticação real confirmada com Keycloak;
- [x] heartbeat, polling, confirmação e resultado;
- [x] fila persistente;
- [x] reinício exige login.
- [x] empresa, cliente e múltiplos projetos podem ser criados pelo agente;
- [x] tarefas HTTP permanecem vivas até entregar sucesso ou falha à interface;
- [x] instalação é identificada automaticamente após login, sem conexão ou aprovação manual;
- [x] falha transitória da sessão técnica é repetida automaticamente;
- [x] botão de autenticação apresentado como `LOGIN`;
- [x] botão `Selecionar HD` permite analisar uma mídia inteira;
- [x] cada análise exige escolher a mídia ou pasta de destino;
- [x] último destino é apenas sugerido e destinos dentro da origem são bloqueados;
- [x] estrutura `Cliente/Projeto/Ano/Mês/Dia` calculada sem botão de destino;
- [ ] revalidar visualmente login e sessão automática com o código-fonte atual;
- [ ] recompilar o instalador com as correções mais recentes.

## Fase 3 — análise e prévia

- [x] seleção, metadados básicos e checksum em streaming;
- [x] conflitos e duplicidades;
- [x] prévia obrigatória e recuperável;

## Fase 4 — organização local segura

- [x] exclusão e sobrescrita proibidas;
- [x] checkpoints e retomada segura;
- [x] catálogo sem caminho completo;
- [x] frontend aberto na operação correta.

## Fase 5 — frontend

- [x] React/TypeScript/Vite;
- [x] login e contexto empresarial;
- [ ] clientes, projetos e acessos;
- [x] catálogo e tags;
- [ ] operações pelo frontend; gestão de máquinas não é requisito funcional;
- [ ] fila, progresso, erros e auditoria;
- [ ] fluxo adequado a usuário não técnico.

## Fase 6 — Drive

- [x] contratos de armazenamento e adaptador local simulado;
- [x] histórico de conta e modelos de lote, item, tentativa e checkpoint;
- [x] OAuth `drive.file` validado com conta real de teste;
- [x] pasta raiz isolada e árvore idempotente `Empresa/Projeto/AAAA.MM/DD/categoria`;
- [x] estado OAuth temporário, uso único e callback exclusivo do backend;
- [x] refresh token criptografado e isolado por empresa;
- [x] persistência e monotonicidade de checkpoint no backend;
- [x] criação, consulta e renovação segura da sessão retomável no backend;
- [x] ensaio da sessão retomável no Google Drive real;
- [x] upload direto agente–Drive em blocos com checkpoint SQLite;
- [x] renovação automática após expiração da sessão;
- [x] URL retomável ausente do SQLite e dos resultados de comando;
- [x] tamanho e SHA-256 verificados antes do transporte;
- [x] pausa, retomada e cancelamento no próximo bloco seguro;
- [x] confirmação central idempotente de integridade e objeto implementada;
- [x] catálogo sincronizado somente após validação central;
- [x] confirmação ensaiada contra objeto real do Drive;
- [x] frontend inicia e acompanha a conexão sem receber credenciais persistentes;
- [x] frontend cria lote e acompanha progresso geral e por arquivo;
- [x] frontend oferece pausa, retomada e cancelamento;
- [x] recarregar a página recupera o estado central do lote;
- [x] erros de autenticação, internet, disco, cota e integridade são acionáveis;
- [x] frontend nunca expõe refresh token ou URL retomável.
- [x] ensaio OAuth real com credenciais e conta Google de teste.

## Fase 7 — tempo real e reconciliação

- [x] WebSocket com polling de fallback;
- [x] presença e progresso não regressivo;
- [x] reconciliação entre as três fontes no fluxo retomável;
- [x] ingresso de uso único e revogação de canal após bloqueio do usuário;
- [ ] auditoria e alertas.

## Fase 8 — entrega

- [ ] E2E no Windows;
- [ ] retomada, desconexão e isolamento validados;
- [x] segurança do ingresso WebSocket e segredos automatizada;
- [ ] backup e restauração ensaiados; rotinas e verificação SHA-256 implementadas;
- [ ] Docker, manual e limitações publicados;
- [ ] release do MVP criada.
