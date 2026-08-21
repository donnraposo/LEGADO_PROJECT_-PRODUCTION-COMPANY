# Frontend LEGADO

Interface operacional do MVP em React, TypeScript e Vite.

A identidade visual inicial utiliza verde, branco e preto, com tons neutros somente
para hierarquia, bordas e estados auxiliares.

## Desenvolvimento

```powershell
pnpm install
pnpm run generate:api
pnpm run dev
```

O Vite encaminha `/api` ao backend local. A autenticação usa o cliente público
`legado-web` do Keycloak com Authorization Code e PKCE S256. Tokens permanecem apenas
em memória.

O serviço também integra a composição em `infrastructure/docker/compose.dev.yaml` e
é iniciado com o perfil `identity` em `http://127.0.0.1:5173`.

## Validação

```powershell
pnpm run typecheck
pnpm test
pnpm run build
```
