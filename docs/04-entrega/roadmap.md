# Estado e roadmap

> A primeira entrega funcional agora é controlada pelo [Roadmap do MVP](roadmap-mvp.md) e pelo [Checklist do MVP](checklist-mvp.md). Este documento permanece como visão histórica e roadmap amplo do produto.

> Para retomada por outra pessoa ou IA, use [Continuidade do MVP](continuidade-mvp.md).

**Atualizado em:** 25 de agosto de 2026.

## Concluído e aprovado

- visão, regras de negócio e requisitos não funcionais iniciais;
- stack do frontend, backend e agente local;
- Clean Architecture, Clean Code, SOLID e uma classe por arquivo;
- autenticação e comunicação agente–backend;
- arquitetura de OAuth e upload retomável no Google Drive;
- estratégia inicial sem serviços pagos obrigatórios;
- responsabilidades e contratos do n8n;
- filas, retomada, concorrência e idempotência;
- modelo conceitual PostgreSQL;
- contratos REST e OpenAPI 3.1;
- documentação fragmentada por categorias;
- monorepo, módulos e dependências entre camadas;
- persistência PostgreSQL externa aos containers;
- esteira de atualização, migrations seguras e rollback da aplicação;
- política inicial de backup e recuperação.

## Próxima etapa

OAuth real do Google Drive concluído. A próxima etapa executável é criar a estrutura
idempotente de pastas, modelar lotes e preparar o upload retomável direto do agente.

### Implementação incremental em andamento

- concluída a base inicial de identidade e empresas;
- implementada a primeira fatia de clientes, projetos e acesso empresarial;
- concluídos convites, gestão básica de membros e atribuição de projetos;
- concluídas auditoria administrativa imutável e entrega assíncrona de convites;
- concluídas consulta de auditoria e concorrência otimista inicial para membros;
- em andamento a migração das demais operações para casos de uso e portas;
- concluída a migração de alteração de membros e acessos de projeto para casos de uso.
- concluída a migração do aceite de convites para caso de uso e portas.
- concluída a migração do cancelamento de convites para caso de uso e portas.
- concluída a migração de criação e listagem de convites para casos de uso e portas.
- concluída a evolução dos eventos com nome, descrição e diferenças campo a campo.
- concluída a retirada de ORM e transações dos adaptadores HTTP administrativos;
- concluída a proteção da auditoria diretamente no PostgreSQL;
- concluído o rastreamento de tentativas e resultados de e-mail;
- validado o fluxo Django, Redis, Celery e Mailpit.

### Próxima fatia funcional

- iniciados catálogo audiovisual, metadados e versões físicas;
- concluídos histórico de metadados e primeira entrega de tags;
- concluídos busca, filtros e paginação inicial por cursor;
- concluídos estados de disponibilidade, reconciliação e auditoria de tags;
- iniciados registro de máquinas, presença e comandos persistidos idempotentes;
- concluídos confirmação, progresso e resultado com concorrência otimista;
- integrado o resultado de reconciliação ao estado técnico do catálogo;
- concluído o esqueleto funcional do agente local com SQLite, OIDC/PKCE, presença e fila;
- validar o agente ponta a ponta com Python 3.14 e Keycloak local;
- implementadas análise, checksum, conflitos e prévia local recuperável;
- validar a interface em Python 3.14 e arquitetar a organização local segura;
- próxima implementação: confirmação, resolução de conflitos, checkpoints e movimentação sem sobrescrita;
- concluída a organização local segura com confirmação, checkpoints e retomada;
- implementado o frontend inicial com autenticação, catálogo e painel do Drive;
- validada a conexão OAuth com uma conta Google real;
- próxima implementação: árvore idempotente de pastas, histórico de contas e lotes.

Concluir a infraestrutura além da base local já validada:

1. Docker para produção;
2. validação funcional de Keycloak, Celery, Channels e n8n;
3. armazenamento local de prévias e alternativa S3 compatível;
4. hospedagem inicial sem custos obrigatórios;
5. logs técnicos, métricas, rastreamento e alertas;
6. transformar a política aprovada de backup e recuperação em procedimentos executáveis.

## Depois da base atual

1. concluir pastas, lotes e upload retomável;
2. adicionar acompanhamento em tempo real e comandos de pausa, retomada e cancelamento;
3. concluir aprovações, compartilhamento e downloads;
4. executar a validação integral do MVP e preparar a operação piloto.

## Pendências conhecidas

- validação futura com Google Workspace e Drive Compartilhado;
- revisão de licenças antes da primeira produtora externa;
- detalhamento da composição Docker e armazenamento S3 compatível opcional;
- procedimento operacional de backup e recuperação;
- fechamento dos módulos de upload, aprovações e downloads.

## Autorização

A estrutura arquitetural e o início da implementação foram aprovados explicitamente. Mudanças arquiteturais continuam sujeitas a nova aprovação.
