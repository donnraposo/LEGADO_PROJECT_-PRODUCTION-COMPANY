# Stack tecnológica

Tecnologias aprovadas e justificativa da composição.

> Origem: documento mestre v0.12. As numerações originais foram mantidas para rastreabilidade.

## 35. Direções e tecnologias aprovadas

- frontend online;
- backend central;
- PostgreSQL para catálogo, estados e auditoria;
- n8n como orquestrador;
- Google Drive como armazenamento de arquivos;
- upload direto e retomável do agente local ao Drive;
- Docker para os componentes de servidor;
- agente local com acesso controlado ao sistema de arquivos;
- comunicação segura iniciada pelo agente, sem expor portas da máquina à internet;
- metadados no backend, binários fora dele.


### Stack principal aprovada

#### Frontend

- React;
- TypeScript;
- Vite;
- aplicação online separada do backend.

#### Backend central

- Python 3.14;
- Django 5.2 LTS;
- Django REST Framework para APIs;
- Daphne como servidor ASGI;
- PostgreSQL para persistência principal;
- Redis para cache, filas e eventos;
- Celery para tarefas assíncronas;
- Celery Beat para agendamentos;
- Django Channels com `channels_redis` para comunicação em tempo real;
- Keycloak por OpenID Connect para autenticação e sessões;
- n8n para integrações e automações leves;
- execução dos componentes de servidor em Docker.

#### Agente local

- Python 3.14;
- PySide6/Qt para a interface desktop;
- SQLite para fila local persistente;
- comunicação HTTP e WebSocket iniciada pelo agente;
- nova autenticação obrigatória após reinício do computador, sem restauração automática da sessão local;
- operações pesadas separadas da thread da interface;
- processamento e checksum sempre em streaming;
- empacotamento planejado com `pyside6-deploy` e Nuitka;
- prioridade inicial para Windows e preparação para macOS.

#### Armazenamento

- Google Drive para arquivos originais enviados;
- armazenamento de objetos compatível com S3 para miniaturas, prévias e artefatos temporários, sujeito ao detalhamento da implantação;
- PostgreSQL não armazenará os grandes binários.


### Justificativa resumida

- Django foi escolhido pela maturidade em regras transacionais, autenticação integrada, ORM, administração e segurança;
- Django REST Framework fornecerá a API consumida pelo frontend e pelo agente;
- Celery e Redis separarão tarefas demoradas do ciclo HTTP;
- Channels entregará progresso e alertas em tempo real;
- Python e PySide6 permitirão compartilhar linguagem e conhecimento entre backend e agente;
- o núcleo do agente permanecerá separado da interface para preservar responsividade e confiabilidade;
- arquivos grandes continuarão fora do backend, enviados diretamente pelo agente ao Drive.


