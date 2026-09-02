# Backup e restauração

Execute com o agente local fechado. O backup inclui PostgreSQL, Keycloak e n8n; informe o
caminho do `agent.sqlite3` para incluir também o estado local retomável.

```powershell
./infrastructure/operations/backup.ps1 -Destination D:/Backups -AgentDatabase D:/dados/agent.sqlite3
./infrastructure/operations/restore.ps1 -Backup D:/Backups/legado-AAAAMMDD-HHMMSS -ConfirmRestore RESTAURAR -AgentDatabase D:/dados/agent.sqlite3
```

A restauração valida SHA-256 antes de alterar os bancos. Use somente em ambiente parado e
faça um novo backup antes de restaurar.
