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

## Fase 1 — catálogo

- [x] estados técnicos e reconciliação autenticada pelo agente;
- [x] auditoria de tags e estados;
- [x] histórico consultável e restaurável;
- [x] filtros restantes e tags nas respostas;
- [x] contratos e testes aprovados.

## Fase 2 — agente mínimo

- [x] scaffold Python/PySide6;
- [x] instalação identificada e SQLite migrável;
- [ ] login OIDC/PKCE implementado; falta ensaio manual com o Keycloak ativo;
- [x] heartbeat, polling, confirmação e resultado;
- [x] fila persistente;
- [x] reinício exige login.

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
- [ ] login e contexto empresarial;
- [ ] clientes, projetos e acessos;
- [ ] catálogo, tags, máquinas e operações;
- [ ] fila, progresso, erros e auditoria;
- [ ] fluxo adequado a usuário não técnico.

## Fase 6 — Drive

- [ ] OAuth `drive.file` e pasta isolada;
- [ ] sessão retomável e checkpoint;
- [ ] upload direto agente–Drive;
- [ ] pausa, retomada e cancelamento;
- [ ] integridade e objeto do Drive confirmados;
- [ ] catálogo sincronizado sem duplicação.

## Fase 7 — tempo real e reconciliação

- [ ] WebSocket com polling de fallback;
- [ ] presença e progresso não regressivo;
- [ ] reconciliação entre as três fontes;
- [ ] auditoria e alertas.

## Fase 8 — entrega

- [ ] E2E no Windows;
- [ ] retomada, desconexão e isolamento validados;
- [ ] segurança revisada;
- [ ] backup e restauração ensaiados;
- [ ] Docker, manual e limitações publicados;
- [ ] release do MVP criada.
