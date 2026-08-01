# Clean Architecture e SOLID

Padrões obrigatórios, limites de camadas e organização das classes.

> Origem: documento mestre v0.12. As numerações originais foram mantidas para rastreabilidade.

### Padrões arquiteturais obrigatórios

- todo o projeto seguirá Clean Architecture, Clean Code e princípios SOLID;
- regras de negócio ficarão independentes de Django, PySide6, banco de dados, filas, n8n e Google Drive;
- dependências sempre apontarão das camadas externas para as camadas internas;
- cada caso de uso terá responsabilidade única e contrato explícito;
- controllers, views, serializers, consumers, comandos da interface e tarefas Celery serão adaptadores finos;
- decisões de negócio não poderão ficar em views, serializers, consumers, tarefas Celery ou workflows do n8n;
- integrações externas serão acessadas por interfaces definidas nas camadas internas e implementadas na infraestrutura;
- cada classe terá seu próprio arquivo, com nome explícito e responsabilidade única;
- no frontend, cada componente, hook, serviço ou unidade principal terá arquivo próprio;
- arquivos e módulos deverão permanecer pequenos, coesos e fáceis de localizar;
- arquivos genéricos como `utils`, `helpers` ou `services` não poderão concentrar responsabilidades sem um domínio claramente identificado;
- não serão criadas abstrações sem necessidade concreta;
- código gerado automaticamente, migrations e arquivos declarativos de configuração não estarão sujeitos à regra de uma classe por arquivo;
- testes acompanharão os mesmos limites arquiteturais e validarão domínio, casos de uso e adaptadores separadamente.


### Camadas lógicas

```text
Domínio
└── entidades, objetos de valor, regras e eventos

Aplicação
└── casos de uso, contratos, comandos e consultas

Adaptadores
└── API, interface desktop, WebSocket, Celery e presenters

Infraestrutura
└── Django ORM, PostgreSQL, Redis, Keycloak, Drive, n8n, SQLite e sistema operacional
```

O backend Django e o agente Python possuirão seus próprios limites de domínio e aplicação. Contratos de comunicação serão versionados, mas nenhuma camada compartilhará diretamente modelos de persistência da outra.


