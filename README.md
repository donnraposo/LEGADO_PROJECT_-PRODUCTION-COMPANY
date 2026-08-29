# Gerenciador de Áudio Visual — Plataforma de Produção Audiovisual

Plataforma para organização local, catalogação, upload retomável e gestão segura de acervos audiovisuais.

## Estado

O MVP está em implementação. A base de identidade, empresas, projetos, catálogo,
operações, agente local, frontend, OAuth, árvore de pastas do Google Drive e persistência
idempotente de lotes, sessões retomáveis e envio direto em blocos já foi construída.
A próxima entrega é repetir o ensaio real e implementar a interface de lotes.

Para retomar o desenvolvimento, comece por [Continuidade do MVP](docs/04-entrega/continuidade-mvp.md)
e depois consulte o [índice arquitetural](PROJETO_AUDIOVISUAL.md).

## Stack aprovada

- frontend: React, TypeScript e Vite;
- backend: Python, Django, Django REST Framework e Daphne;
- agente local: Python e PySide6;
- dados: PostgreSQL, Redis e SQLite local no agente;
- tarefas e tempo real: Celery, Celery Beat, Django Channels e WebSocket;
- identidade: Keycloak com OpenID Connect;
- arquivos originais: Google Drive com upload retomável direto;
- automações internas: n8n Community;
- componentes de servidor: Docker.

## Estrutura

- `backend`: API, domínio e processamento central;
- `agent`: aplicativo local e fila persistente;
- `web`: frontend online;
- `contracts`: OpenAPI e eventos versionados;
- `automation`: workflows internos;
- `infrastructure`: containers, ambientes e operação;
- `docs`: regras, arquitetura, decisões e entrega.

## Segurança

Segredos, tokens, bancos locais, backups, volumes e arquivos audiovisuais não devem ser armazenados junto ao código. Consulte [Persistência, deploy e migrations](docs/03-arquitetura/persistencia-deploy-migracoes.md).

## Licença

Nenhuma licença pública foi definida. O projeto deve permanecer privado até decisão formal de licenciamento e comercialização.
