# Agente local

Aplicativo Windows em Python 3.14 e PySide6 responsável pela fila local e pela execução autenticada de comandos persistidos pelo backend.

## Estado do MVP

- identificador persistente da instalação;
- SQLite migrável com fila idempotente;
- login OIDC Authorization Code + PKCE no navegador;
- token somente em memória;
- heartbeat e vínculo da máquina por empresa;
- polling incremental e confirmação de comandos;
- execução segura do comando `PING` e falha explícita para comandos ainda não suportados;
- interface mínima de sessão, empresa, presença e fila.
- seleção autenticada de cliente, projeto, arquivos e pastas;
- análise somente leitura com exclusão de itens técnicos;
- SHA-256 em streaming e detecção de duplicidades e conflitos;
- prévia selecionável e recuperável armazenada no SQLite;
- destino explícito, confirmação e resolução de conflitos;
- movimentação sem sobrescrita, inclusive entre volumes com verificação SHA-256;
- checkpoints, interrupção e retomada sem repetir arquivos concluídos;
- catálogo central idempotente sem envio de caminhos locais.

## Configuração

Variáveis opcionais:

```text
LEGADO_BACKEND_URL=http://127.0.0.1:8000
LEGADO_OIDC_ISSUER=http://127.0.0.1:8080/realms/legado
LEGADO_OIDC_CLIENT_ID=legado-agent
LEGADO_DATA_DIR=<diretório local do agente>
LEGADO_POLL_INTERVAL=5
LEGADO_WEB_URL=http://127.0.0.1:5173
```

O SQLite nunca armazena senha, token OIDC ou credencial do Drive. Encerrar o agente descarta a sessão e o próximo início exige novo login.

Os caminhos locais completos existem somente no SQLite do agente. A análise não altera
arquivos. A organização somente começa após confirmação explícita, nunca substitui um
destino e mantém checkpoint local antes e depois de cada movimentação.

O ambiente Docker importa, na primeira inicialização do Keycloak, o realm `legado` e
o cliente público `legado-agent` configurado para PKCE S256.

## Desenvolvimento

```powershell
python -m pip install -e ".[dev]"
ruff check .
pytest
legado-agent
```

O requisito oficial é Python 3.14. A validação automatizada desta etapa também foi
executada no runtime auxiliar Python 3.12, sem alterar o requisito do produto.
