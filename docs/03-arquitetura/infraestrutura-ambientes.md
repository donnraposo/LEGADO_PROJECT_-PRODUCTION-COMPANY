# Infraestrutura e ambientes

**Estado:** IMPLEMENTAÇÃO INICIAL VALIDADA.

Este documento concentra as decisões de infraestrutura. A persistência durante atualizações já está aprovada; composição completa dos serviços, hospedagem e observabilidade ainda serão concluídas.

## Princípios aprovados

- containers da aplicação serão substituíveis e não armazenarão estado permanente;
- PostgreSQL manterá seus dados fora da camada gravável do container;
- cada ambiente terá recursos, nomes e segredos próprios;
- atualização da aplicação não recriará o banco nem restaurará backups desnecessariamente;
- ausência de armazenamento esperado interromperá a implantação;
- infraestrutura local e hospedada deverão ser reproduzíveis;
- comandos destrutivos sobre volumes não farão parte da esteira normal.

## Ambientes

| Ambiente | Finalidade | Dados |
|---|---|---|
| desenvolvimento | construção e testes locais | dados descartáveis ou anonimizados |
| teste automatizado | validação isolada da esteira | criado e removido por execução |
| piloto | validação com a primeira produtora | persistente, sensível e com backup |
| produção | operação comercial futura | persistente, redundante e com recuperação contínua |

Dados de produção não poderão ser copiados para desenvolvimento sem anonimização aprovada.

## Persistência

As regras completas estão em [Persistência, deploy e migrations](persistencia-deploy-migracoes.md).

- volumes serão nomeados explicitamente por ambiente;
- o volume PostgreSQL de piloto ou produção será externo ao ciclo de vida do Compose;
- a esteira deverá encontrar o volume já provisionado;
- nenhum banco vazio será criado silenciosamente quando o armazenamento esperado estiver ausente;
- volumes e backups possuirão controles de acesso próprios.

## Estado da infraestrutura

### Aprovado

- separação entre container e dados;
- atualização segura da aplicação;
- migrations compatíveis com rollback da aplicação;
- backup anterior a mudanças críticas;
- recuperação controlada e testes de restauração.

### Implementado no desenvolvimento

- Docker Compose com PostgreSQL, Redis, Django/Daphne e Celery;
- perfis opcionais para Keycloak e n8n;
- volumes externos com nomes estáveis;
- migração isolada e verificações de vida e prontidão;
- recriação real do container PostgreSQL preservando os dados.

### Pendente

- composição de produção;
- proxy e exposição de rede;
- hospedagem do piloto;
- observabilidade técnica;
- dimensionamento inicial;
- estratégia comercial de alta disponibilidade.

## Referências

- [Persistência de dados com volumes Docker](https://docs.docker.com/engine/storage/volumes/)
- [Atualização de clusters PostgreSQL](https://www.postgresql.org/docs/16/upgrading.html)
