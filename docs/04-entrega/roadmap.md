# Estado e roadmap

**Atualizado em:** 1º de agosto de 2026.

## Concluído e aprovado

- visão, regras de negócio e requisitos não funcionais iniciais;
- stack do frontend, backend e agente local;
- Clean Architecture, Clean Code, SOLID e uma classe por arquivo;
- autenticação e comunicação agente–backend;
- integração OAuth e upload retomável no Google Drive;
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

### Implementação incremental em andamento

- concluída a base inicial de identidade e empresas;
- implementada a primeira fatia de clientes, projetos e acesso empresarial;
- concluídos convites, gestão básica de membros e atribuição de projetos;
- próximo incremento: auditoria das operações administrativas e entrega de e-mail.

Concluir a infraestrutura além da base local já validada:

1. Docker para produção;
2. validação funcional de Keycloak, Celery, Channels e n8n;
3. armazenamento local de prévias e alternativa S3 compatível;
4. hospedagem inicial sem custos obrigatórios;
5. logs técnicos, métricas, rastreamento e alertas;
6. transformar a política aprovada de backup e recuperação em procedimentos executáveis.

## Depois da infraestrutura

1. metodologia e plano incremental de implementação;
2. plano detalhado de testes e critérios de aceite por etapa;
3. preparação dos ambientes;
4. criação controlada do esqueleto do monorepo;
5. implementação por módulos e casos de uso.

## Pendências conhecidas

- validação futura com Google Workspace e Drive Compartilhado;
- revisão de licenças antes da primeira produtora externa;
- detalhamento da composição Docker e armazenamento S3 compatível opcional;
- plano detalhado de testes;
- implementação dos módulos de domínio.

## Autorização

A estrutura arquitetural e o início da implementação foram aprovados explicitamente. Mudanças arquiteturais continuam sujeitas a nova aprovação.
