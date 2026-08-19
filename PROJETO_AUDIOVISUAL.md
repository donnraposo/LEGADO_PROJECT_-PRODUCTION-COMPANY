# Projeto Audiovisual

Índice conciso da documentação arquitetural. Leia somente os blocos relacionados à tarefa atual.

## Estado atual

- Regras de negócio, stack, autenticação, comunicação, Drive, n8n, filas, modelo de dados e contratos de API: **aprovados**.
- Monorepo, módulos e dependências entre camadas: **aprovados**.
- Implementação do software: **iniciada e autorizada em 1º de agosto de 2026**.
- Fases 0 e 1 do MVP: **validadas**.
- Fases 2 e 3 do MVP: **implementadas e aguardando validação funcional**.
- Próxima implementação: **Fase 4 — organização local segura**.
- Documento original: [monólito v0.12 preservado](docs/arquivo/PROJETO_AUDIOVISUAL_MONOLITO_v0.12.md).

## Leitura rápida

### Produto

- [Visão e objetivos](docs/01-produto/visao-e-objetivos.md)
- [Requisitos não funcionais](docs/01-produto/requisitos-nao-funcionais.md)

### Regras de negócio

- [Mapa das regras complementares](docs/02-regras-negocio/regras-complementares.md)
- [Empresas, usuários e autenticação](docs/02-regras-negocio/empresas-usuarios-autenticacao.md)
- [Clientes, projetos e permissões](docs/02-regras-negocio/clientes-projetos-permissoes.md)
- [Organização local](docs/02-regras-negocio/organizacao-local.md)
- [Catálogo, metadados e tags](docs/02-regras-negocio/catalogo-metadados-tags.md)
- [Uploads, aprovações e Drive](docs/02-regras-negocio/uploads-aprovacoes-drive.md)
- [Downloads e lixeira](docs/02-regras-negocio/downloads-lixeira.md)
- [Auditoria, notificações e conformidade](docs/02-regras-negocio/auditoria-notificacoes-conformidade.md)

### Arquitetura

- [Visão geral](docs/03-arquitetura/visao-geral.md)
- [Stack tecnológica](docs/03-arquitetura/stack-tecnologica.md)
- [Clean Architecture e SOLID](docs/03-arquitetura/clean-architecture-solid.md)
- [Autenticação e comunicação](docs/03-arquitetura/autenticacao-comunicacao.md)
- [Google Drive](docs/03-arquitetura/google-drive.md)
- [n8n](docs/03-arquitetura/n8n.md)
- [Filas, retomada e idempotência](docs/03-arquitetura/filas-retomada-idempotencia.md)
- [Modelo de dados](docs/03-arquitetura/modelo-dados.md)
- [Contratos de API](docs/03-arquitetura/contratos-api.md)
- [Estrutura do repositório](docs/03-arquitetura/estrutura-repositorio.md)
- [Infraestrutura e ambientes](docs/03-arquitetura/infraestrutura-ambientes.md)
- [Persistência, deploy e migrations](docs/03-arquitetura/persistencia-deploy-migracoes.md)

### Entrega e continuidade

- [Continuidade operacional do MVP](docs/04-entrega/continuidade-mvp.md)
- [Roadmap do MVP](docs/04-entrega/roadmap-mvp.md)
- [Checklist do MVP](docs/04-entrega/checklist-mvp.md)
- [Estado e roadmap](docs/04-entrega/roadmap.md)
- [Estado detalhado da implementação](docs/04-entrega/estado-implementacao.md)
- [Plano de testes](docs/04-entrega/plano-testes.md)
- [Critérios de aceite](docs/04-entrega/criterios-aceite.md)
- [Operação e recuperação](docs/04-entrega/operacao-recuperacao.md)
- [Decisões e continuidade](docs/decisoes/registro-decisoes.md)

## Regra para IA ou novo responsável

1. Comece pela [continuidade do MVP](docs/04-entrega/continuidade-mvp.md) e por este índice.
2. Abra apenas os documentos ligados à atividade atual.
3. Decisões marcadas como aprovadas são requisitos vigentes.
4. Não altere decisões arquiteturais sem explicar o impacto e obter aprovação.
5. Não implemente código ou estrutura sem aprovação explícita.
6. Registre novas decisões no bloco temático correspondente e no [registro de decisões](docs/decisoes/registro-decisoes.md).

## Próxima etapa

Fechar os ensaios funcionais das Fases 2 e 3 e arquitetar a Fase 4. A próxima
implementação deve adicionar confirmação explícita, resolução de conflitos,
checkpoints e movimentação local sem exclusão ou sobrescrita.
