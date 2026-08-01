# Estrutura do repositório e módulos

**Estado:** APROVADO em 31 de julho de 2026.

## Decisões estruturais

- monorepo para manter backend, agente, frontend, contratos e infraestrutura sincronizados;
- backend como monólito modular Django;
- organização primeiro por domínio funcional e depois por camada;
- Clean Architecture aplicada separadamente ao backend e ao agente;
- frontend organizado por módulos funcionais;
- uma classe ou unidade principal por arquivo, respeitadas as exceções já aprovadas;
- contratos de comunicação versionados e isolados dos modelos de persistência;
- nenhum módulo poderá acessar diretamente modelos ORM de outro módulo.

Microserviços e múltiplos repositórios não serão adotados nesta fase. Eles aumentariam custo operacional, complexidade de observabilidade e risco de inconsistência sem benefício proporcional para a primeira produtora.

## Estrutura de alto nível

```text
/
├── backend/
│   ├── src/
│   │   ├── config/
│   │   ├── shared/
│   │   └── modules/
│   └── tests/
├── agent/
│   ├── src/
│   │   ├── config/
│   │   ├── shared/
│   │   └── modules/
│   └── tests/
├── web/
│   ├── src/
│   │   ├── app/
│   │   ├── shared/
│   │   └── modules/
│   └── tests/
├── contracts/
│   ├── openapi/
│   ├── events/
│   └── generated/
├── automation/
│   └── n8n/
├── infrastructure/
│   ├── docker/
│   ├── keycloak/
│   ├── database/
│   └── observability/
└── docs/
```

## Backend Django

### Módulos funcionais iniciais

```text
backend/src/modules/
├── identity/
├── companies/
├── projects/
├── catalog/
├── uploads/
├── approvals/
├── downloads/
├── drive/
├── notifications/
├── audit/
└── integrations/
```

Cada módulo será uma unidade funcional independente. A divisão não representa microserviços e não autoriza bancos separados.

### Estrutura interna de um módulo

```text
module/
├── domain/
│   ├── entities/
│   ├── value_objects/
│   ├── events/
│   └── exceptions/
├── application/
│   ├── commands/
│   ├── queries/
│   ├── use_cases/
│   ├── dto/
│   └── ports/
├── adapters/
│   ├── api/
│   ├── tasks/
│   ├── consumers/
│   └── presenters/
├── infrastructure/
│   ├── persistence/
│   └── integrations/
├── migrations/
└── apps.py
```

As convenções obrigatórias do Django poderão permanecer na raiz do módulo, mas serão tratadas como detalhes externos. Modelos ORM não serão entidades de domínio. Quando o Django exigir descoberta por convenção, arquivos de inicialização apenas reexportarão os modelos, sem regras de negócio.

### Dependências permitidas

```text
adapters ───────► application ───────► domain
infrastructure ─► application ───────► domain
config ─────────► todas, somente para composição
```

- `domain` não importa Django, DRF, Celery, Redis, Drive ou banco de dados;
- `application` conhece o domínio e define portas para recursos externos;
- `infrastructure` implementa as portas da aplicação;
- `adapters` traduz HTTP, WebSocket, Celery e outros transportes;
- `config` é a raiz de composição e conecta implementações a contratos;
- comunicação entre módulos ocorre por casos de uso, contratos públicos ou eventos;
- imports diretos de repositórios, ORM ou infraestrutura de outro módulo são proibidos.

## Agente local

```text
agent/src/modules/
├── authentication/
├── filesystem/
├── organization/
├── uploads/
├── synchronization/
└── desktop_ui/
```

Os módulos do agente usarão as mesmas camadas de domínio, aplicação, adaptadores e infraestrutura. `desktop_ui` será um adaptador PySide6 e não conterá regras de negócio. Sistema de arquivos, SQLite, HTTP e WebSocket serão implementações de portas internas.

## Frontend

```text
web/src/
├── app/
├── shared/
└── modules/
    ├── authentication/
    ├── companies/
    ├── projects/
    ├── catalog/
    ├── uploads/
    ├── approvals/
    ├── downloads/
    ├── notifications/
    └── audit/
```

Cada módulo poderá conter `components`, `pages`, `hooks`, `services`, `schemas` e `tests`, criados somente quando necessários. Componentes, hooks e serviços principais terão arquivos próprios. Clientes OpenAPI gerados ficarão isolados e não serão editados manualmente.

## Contratos e automações

- `contracts/openapi`: especificação OpenAPI 3.1 versionada;
- `contracts/events`: envelopes e esquemas dos eventos de integração;
- `contracts/generated`: clientes e tipos gerados automaticamente;
- `automation/n8n`: workflows exportados, documentação e versões;
- n8n consumirá somente contratos públicos do backend;
- backend, agente e frontend não compartilharão modelos ORM ou entidades internas.

## Código compartilhado

`shared` conterá somente elementos estáveis e usados por mais de um módulo, como identificadores, abstração de relógio, paginação ou erros transversais. São proibidos depósitos genéricos chamados `utils`, `helpers` ou `services` sem responsabilidade explícita.

Uma abstração deverá permanecer no módulo proprietário até existir necessidade concreta de compartilhamento.

## Testes

Cada aplicação terá testes próprios, separados em:

- `unit`: domínio e casos de uso sem infraestrutura;
- `integration`: banco, filas, APIs e integrações adaptadas;
- `architecture`: regras de importação e limites entre camadas;
- `e2e`: fluxos críticos entre componentes.

Os testes seguirão os mesmos limites dos módulos de produção. Testes de arquitetura deverão impedir dependências invertidas e acesso ao ORM de outro módulo.

## Convenções de manutenção

- nomes de arquivos e classes deverão expressar a responsabilidade;
- cada caso de uso terá contrato e responsabilidade únicos;
- nenhuma regra de negócio ficará em view, serializer, consumer, tarefa Celery, componente React ou workflow n8n;
- migrations, configurações declarativas e código gerado permanecem fora da regra de uma classe por arquivo;
- novos módulos exigirão uma responsabilidade funcional clara;
- qualquer mudança nesses limites deverá ser registrada como decisão arquitetural.

## Critérios de aceite da estrutura

- responsabilidade localizável por domínio e camada;
- ausência de dependências circulares;
- domínio executável e testável sem frameworks;
- integrações externas substituíveis por portas;
- contratos versionados e independentes da persistência;
- estrutura preparada para separar serviços futuramente sem impor essa complexidade agora.
