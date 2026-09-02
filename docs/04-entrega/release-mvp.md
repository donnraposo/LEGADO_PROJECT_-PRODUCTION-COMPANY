# Preparação da release do MVP

**Estado:** CANDIDATA LOCAL — NÃO PUBLICADA. Atualizada em 31 de agosto de 2026.

## Incluído

- upload real retomável e controles operacionais;
- painel em português com WebSocket e polling de contingência;
- reconciliação de checkpoints entre Drive, PostgreSQL e SQLite;
- ingresso WebSocket efêmero, de uso único e vinculado à associação ativa;
- rotinas de backup e restauração com manifesto SHA-256.

## Validação concluída

- backend: 66 testes;
- agente: 41 testes;
- frontend: 21 testes, TypeScript e build de produção;
- Ruff aprovado no escopo alterado.

## Bloqueios para publicação

- ensaiar backup e restauração com os serviços parados;
- executar E2E visual completo no Windows, incluindo queda do WebSocket;
- gerar instalador e publicar tag/release somente com autorização explícita.
