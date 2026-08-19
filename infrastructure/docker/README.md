# Ambiente Docker de desenvolvimento

Todos os componentes de servidor serão executados em containers. Não é necessário instalar Python, PostgreSQL, Redis, Keycloak ou n8n diretamente no Windows.

## Preparação

1. Copie `.env.dev.example` para `.env.dev`.
2. Substitua todos os valores iniciados por `change-this`.
3. Nunca compartilhe ou versione `.env.dev`.
4. Provisione uma única vez os volumes externos:

```text
docker volume create legado_postgres_data
docker volume create legado_n8n_data
```

## Serviços principais

```text
docker compose --env-file .env.dev -f compose.dev.yaml up -d postgres redis
docker compose --env-file .env.dev -f compose.dev.yaml --profile tools run --rm migrate
docker compose --env-file .env.dev -f compose.dev.yaml up -d --build backend
```

## Serviços opcionais

```text
docker compose --env-file .env.dev -f compose.dev.yaml --profile identity up -d
docker compose --env-file .env.dev -f compose.dev.yaml --profile automation up -d
```

## Endereços locais

- backend: `http://127.0.0.1:8000`;
- Keycloak, quando ativado: `http://127.0.0.1:8080`;
- n8n, quando ativado: `http://127.0.0.1:5678`.

Na primeira inicialização, o Keycloak importa o realm `legado` e os clientes públicos
`legado-agent` (Authorization Code com PKCE S256) e `legado-api`. O cadastro local de
conta fica disponível na tela de login. A importação não substitui um realm já existente.

## Persistência

PostgreSQL usa o volume externo e estável `legado_postgres_data`. Recriar containers não remove os dados. Se o volume não existir, o ambiente é bloqueado em vez de criar silenciosamente um banco vazio. Não execute `docker compose down -v`, `docker volume prune` nem remova esse volume.
