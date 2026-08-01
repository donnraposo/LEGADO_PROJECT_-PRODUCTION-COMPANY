# Estado da implementação

**Estado:** EM IMPLEMENTAÇÃO desde 1º de agosto de 2026.

Registro operacional do software implementado, das validações executadas, das limitações conhecidas e do ponto obrigatório de continuidade.

> As decisões arquiteturais e regras de negócio permanecem nos documentos temáticos. Este arquivo registra somente o estado concreto da implementação.

## Base executável

### Backend

- projeto Python 3.14 com Django, Django REST Framework e Daphne;
- PostgreSQL como persistência central;
- Redis para cache, canais e filas;
- Celery Worker, fila crítica e Celery Beat previstos na composição local;
- autenticação OIDC com Keycloak e projeção local de usuário;
- endpoints de saúde e erros `application/problem+json`;
- configurações sensíveis fornecidas por ambiente;
- execução dos componentes de servidor em Docker.

### Persistência e desenvolvimento

- volume PostgreSQL externo e estável;
- bloqueio da criação silenciosa de banco vazio;
- serviço separado para migrations;
- Ruff, pytest e verificação de migrations disponíveis no container de desenvolvimento;
- dados reais, segredos e volumes excluídos do repositório.

## Módulos implementados

### Identidade

**Estado:** IMPLEMENTAÇÃO INICIAL VALIDADA.

- validação de token OIDC;
- sincronização da projeção do usuário autenticado;
- e-mail criptografado e índice exato protegido por HMAC;
- endpoint do usuário autenticado.

### Empresas

**Estado:** EM IMPLEMENTAÇÃO.

- criação e listagem de empresas;
- criação automática do vínculo de Proprietário;
- vínculos com papéis `OWNER` e `ADMINISTRATOR`;
- estados `ACTIVE`, `BLOCKED` e `LEFT`;
- convites de uso único com validade de sete dias;
- token de convite persistido somente como resumo SHA-256;
- e-mail do convite criptografado e associado por HMAC;
- aceite restrito à conta autenticada correspondente;
- aceite separado em caso de uso, DTOs, porta e adaptador de persistência;
- aceite, ativação do vínculo e auditoria protegidos pela mesma transação;
- cancelamento e substituição de convite pendente;
- cancelamento separado em caso de uso, porta e adaptador de persistência;
- cancelamento e auditoria protegidos pela mesma transação;
- criação e listagem separadas em casos de uso, portas e adaptadores;
- criação, substituição anterior, auditoria e agendamento protegidos por unidade de trabalho;
- listagem e alteração de membros por Proprietários;
- proteção do último Proprietário ativo;
- concorrência otimista na alteração de membro por `expected_version`;
- conflito de versão retornado como HTTP `409`.

### Clientes e projetos

**Estado:** EM IMPLEMENTAÇÃO.

- criação e listagem de clientes e projetos;
- nome original e normalizado;
- unicidade de cliente por empresa e de projeto por cliente;
- contexto empresarial explícito por `X-Company-ID`;
- isolamento inicial entre empresas;
- acesso automático do Administrador ao projeto criado por ele;
- concessão e revogação de acesso por Proprietários.

### Auditoria

**Estado:** IMPLEMENTAÇÃO INICIAL VALIDADA.

- eventos funcionais para convites, membros e acessos de projeto;
- estado anterior e posterior quando aplicável;
- nome legível e descrição funcional da ação;
- `old_state`, `new_state` e `change_state` persistidos por evento;
- `change_state` calculado automaticamente somente com campos alterados;
- empresa, ator, objeto, correlação e data registrados;
- consulta limitada aos Proprietários da empresa;
- alteração e exclusão por instância bloqueadas no modelo;
- tokens e segredos ausentes dos eventos.

### Notificações

**Estado:** IMPLEMENTAÇÃO INICIAL PARCIAL.

- envio de convite enfileirado por Celery;
- adaptador de e-mail baseado no Django;
- endereço público de aceite e remetente configuráveis;
- política de repetição com atraso progressivo;
- composição do e-mail validada com backend de teste em memória.

## Contratos disponíveis

- saúde do processo e prontidão;
- usuário autenticado;
- empresas;
- clientes e projetos;
- convites e aceite;
- membros;
- concessão e revogação de acesso a projetos;
- consulta de auditoria.

O contrato vigente está em `contracts/openapi/v1.yaml`.

## Migrations existentes

- `identity/0001_initial.py`: projeção de usuários;
- `companies/0001_initial.py`: empresas e vínculos;
- `companies/0002_invitationmodel.py`: convites;
- `projects/0001_initial.py`: clientes, projetos e acessos;
- `audit/0001_initial.py`: eventos funcionais de auditoria;
- `audit/0002_audit_event_details.py`: nome, descrição, estados renomeados e diferenças calculadas.

## Arquitetura aplicada

- monólito modular Django;
- módulos organizados por domínio funcional;
- entidades e objetos de valor sem dependência de framework;
- atualização de membros separada em caso de uso, portas e adaptadores;
- concessão e revogação de acesso a projetos separadas em casos de uso, portas e adaptadores;
- alteração de acesso e respectiva auditoria protegidas pela mesma transação;
- teste arquitetural contra imports de Django, DRF e Celery em `domain` e `application`;
- uma classe ou unidade principal por arquivo, respeitadas as exceções aprovadas.

## Validações executadas

- 26 testes automatizados aprovados;
- lint Ruff aprovado;
- `makemigrations --check --dry-run` sem mudanças pendentes;
- testes de identidade, criptografia, empresas, projetos, convites e permissões;
- testes de isolamento empresarial e proteção do último Proprietário;
- testes de concorrência, auditoria, cálculo de diferenças, e-mail e limites arquiteturais.

## Limitações conhecidas

- listagens e criação de clientes e projetos ainda acessam ORM em views;
- listagem de membros e contexto empresarial ainda acessam ORM em adaptadores HTTP;
- a imutabilidade da auditoria ainda não está reforçada no PostgreSQL contra comandos diretos de `UPDATE` e `DELETE`;
- Celery, Redis e Mailpit ainda precisam de validação funcional conjunta;
- tentativas, falhas e entregas de notificação ainda não possuem persistência própria;
- notificações internas ainda não foram implementadas;
- paginação por cursor ainda não foi implementada;
- Row-Level Security ainda não foi aplicada no PostgreSQL;
- catálogo, agente local, uploads, Drive, frontend, aprovações e downloads permanecem pendentes.

## Próxima etapa obrigatória

Concluir a consolidação arquitetural administrativa:

1. migrar listagens e criação de clientes e projetos para casos de uso e portas;
2. migrar listagem de membros e contexto empresarial para portas próprias;
3. retirar acesso ao ORM dos adaptadores HTTP restantes;
4. ampliar os testes arquiteturais para todos os adaptadores HTTP;
5. reforçar a imutabilidade de auditoria no PostgreSQL;
6. persistir tentativas e resultados de entrega de notificações;
7. validar o fluxo real entre Django, Celery, Redis e Mailpit;
8. atualizar contratos e testes correspondentes.

Depois dessa consolidação, a próxima fatia funcional será o catálogo audiovisual.

## Critérios de aceite da próxima etapa

- views limitadas à tradução HTTP e composição;
- domínio e aplicação independentes de frameworks;
- ORM restrito à infraestrutura de persistência;
- eventos de auditoria protegidos também no banco;
- tentativa, entrega e falha de e-mail rastreáveis;
- nenhum token ou segredo presente em logs ou auditoria;
- lint, migrations e suíte completa aprovados.

## Protocolo de atualização

Ao concluir cada incremento:

1. atualizar o estado do módulo afetado;
2. registrar contratos, migrations e configurações adicionados;
3. registrar somente validações efetivamente executadas;
4. mover itens concluídos para a seção correspondente;
5. manter limitações e próxima etapa coerentes com o código;
6. atualizar também o roadmap, o plano de testes e o registro de decisões quando aplicável;
7. não marcar como concluído o que estiver apenas planejado ou parcialmente validado.

Consulte também [Estado e roadmap](roadmap.md), [Plano de testes](plano-testes.md), [Estrutura do repositório](../03-arquitetura/estrutura-repositorio.md) e [Decisões e continuidade](../decisoes/registro-decisoes.md).
