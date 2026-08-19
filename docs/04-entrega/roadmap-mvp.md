# Roadmap do MVP funcional

**Estado:** EM IMPLEMENTAÇÃO. Atualizado em 19 de agosto de 2026.

**Início:** 3 de agosto de 2026.

Este documento controla a execução do MVP. As regras de negócio e decisões arquiteturais existentes continuam válidas; o MVP reduz a primeira entrega ao fluxo vertical necessário para uso real.

## Objetivo

```text
login → empresa/projeto → seleção local → análise e prévia
→ organização confirmada → catálogo → upload retomável ao Drive
→ verificação → consulta pelo frontend
```

## Escopo obrigatório

- Windows como plataforma inicial do agente;
- uma produtora e uma configuração principal do Drive;
- login OIDC com PKCE;
- empresas, usuários, clientes, projetos e permissões;
- agente local com SQLite e fila persistente;
- análise, checksum e prévia obrigatória;
- organização local sem exclusão ou sobrescrita;
- catálogo, metadados, tags, busca e filtros;
- comandos persistidos e idempotentes;
- upload retomável direto do agente ao Drive;
- frontend mínimo para operar e acompanhar;
- reconciliação, auditoria e Docker local reproduzível.

## Fora do MVP inicial

- macOS e múltiplas contas do Drive;
- n8n como dependência obrigatória do fluxo principal;
- substituição com aprovação e agendamento avançado;
- downloads ZIP, lixeira e restauração completos;
- prévias audiovisuais avançadas;
- S3 opcional, RLS, alta disponibilidade e produção completa.

## Fase 0 — estabilização da base

**Estado:** VALIDADO em 18 de agosto de 2026.

**Baseline de 3 de agosto de 2026:** Ruff aprovado; migrations consistentes e aplicadas; 42 testes aprovados; OpenAPI válido com avisos documentais não bloqueadores. Pendente reconstruir backend e worker com o código atual e verificar a saúde após a recriação.

**Baseline de 18 de agosto de 2026:** backend e workers reconstruídos; PostgreSQL, Redis, backend, workers e Celery Beat operacionais; endpoints `live` e `ready` aprovados; migrations aplicadas sem mudanças pendentes; Ruff aprovado; 42 testes aprovados; OpenAPI válido com 19 avisos documentais não bloqueadores. O arquivo do Celery Beat foi direcionado para `/tmp` para permitir a execução com usuário sem privilégios.

- reativar e verificar Docker;
- aplicar e conferir migrations;
- executar Ruff e a suíte completa;
- validar catálogo, operações e OpenAPI;
- corrigir divergências de código e documentação;
- registrar baseline reproduzível.

**Aceite:** ambiente sobe de forma reproduzível, migrations aplicam em banco vazio e suíte completa fica aprovada.

## Fase 1 — catálogo central utilizável

**Estado:** VALIDADO em 18 de agosto de 2026.

**Incremento validado em 18 de agosto de 2026:** máquina de estados técnicos, reconciliação autenticada por máquina, vínculo da primeira máquina à versão física, repetição idempotente, concorrência otimista, auditoria imutável, restrição PostgreSQL e contrato OpenAPI. Suíte ampliada para 51 testes.

**Fechamento validado em 18 de agosto de 2026:** aplicação e remoção de tags idempotentes e auditadas; tags incluídas nas respostas; histórico paginado e isolado por projeto; restauração como nova versão exclusiva de Proprietários; filtros por extensão, tipo, tamanho, período e responsável; 55 testes, Ruff, migrations, OpenAPI e saúde aprovados.

- estados técnicos e reconciliação vinda do agente;
- auditoria de tags e estados;
- histórico consultável e restauração controlada;
- filtros restantes e tags nas respostas;
- consolidação do OpenAPI.

**Aceite:** arquivos podem ser cadastrados, consultados, editados, classificados e reconciliados sem alteração manual de estado técnico.

## Fase 2 — agente local mínimo

**Estado:** IMPLEMENTADO — AGUARDA VALIDAÇÃO.

**Incremento implementado em 19 de agosto de 2026:** scaffold Python/PySide6 em
camadas, identificação persistente, migrations SQLite, fila idempotente, sessão em
memória, OIDC/PKCE no navegador, heartbeat periódico, polling e ciclo de comandos.
Sete testes e Ruff foram aprovados; a tela Qt iniciou em modo sem exibição. O realm e
os clientes locais do Keycloak foram declarados e a composição Docker foi validada.
Permanece pendente o ensaio manual completo com Python 3.14, conta, empresa e Keycloak
ativos, pois não existe `.env.dev` nesta estação.

- scaffold Python/PySide6 e empacotamento inicial;
- identificador persistente da instalação;
- SQLite e migrations locais;
- login OIDC/PKCE, com token somente em memória;
- heartbeat, polling, confirmação e resultado;
- fila persistente, logs protegidos e interface inicial.

**Aceite:** máquina autentica, aparece online, recebe comando e preserva a fila; reinício exige novo login.

## Fase 3 — análise e prévia local

**Estado:** IMPLEMENTADO — AGUARDA VALIDAÇÃO.

**Incremento implementado em 19 de agosto de 2026:** seleção de arquivos e pastas,
exclusão de itens técnicos, metadados básicos, data do sistema de arquivos, tipo MIME,
checksum SHA-256 em streaming, duplicidades, conflitos de destino, normalização de
segmentos Windows e prévia selecionável persistida no SQLite. Cancelamento ocorre no
próximo arquivo e preserva a prévia parcial. A implementação não contém operação de
movimentação. Ruff e 17 testes foram aprovados no runtime auxiliar Python 3.12,
incluindo preservação de conteúdo e horário da origem, recuperação após reinício e
upgrade do banco local. Permanecem pendentes o ensaio manual em Python 3.14 e a
extração avançada da data original de câmera para formatos compatíveis.

- seleção de pasta e arquivos;
- exclusão de itens técnicos da análise;
- nome, extensão, tipo, tamanho, data e origem da data;
- checksum em streaming;
- conflitos e duplicidades;
- destino Cliente/Projeto/Ano/Mês/Dia;
- prévia obrigatória com seleção de itens.

**Aceite:** análise não modifica arquivos e produz prévia completa e recuperável.

## Fase 4 — organização local segura

**Estado:** EM IMPLEMENTAÇÃO — NÚCLEO IMPLEMENTADO EM 19 DE AGOSTO DE 2026.

**Incremento implementado:** destino confirmado antes da análise; decisões explícitas
para conflitos; uma operação ativa; movimentação sem substituição; cópia em streaming
com SHA-256 entre volumes; checkpoints SQLite; recuperação de queda; interrupção
entre arquivos; e ingestão idempotente no catálogo sem caminho local. Ruff e 25 testes
do agente foram aprovados. O backend passou em Ruff e nos testes arquiteturais; sua
nova integração Django e migration aguardam o ambiente Docker.

- confirmação explícita e uma operação por máquina;
- diretórios e movimentação sem sobrescrita;
- resolução segura de conflitos;
- checkpoints por arquivo;
- interrupção e nova análise após desconexão;
- catálogo sem caminho local completo;
- abertura do frontend na operação correta.

**Aceite:** nenhum arquivo é apagado ou sobrescrito e retomada não repete movimentações concluídas.

## Fase 5 — frontend operacional mínimo

**Estado:** PLANEJADO.

- React, TypeScript e Vite;
- login e seleção de empresa;
- clientes, projetos, membros e acessos;
- catálogo, detalhe, edição e tags;
- máquinas, operações, fila, progresso, erros e auditoria.

**Aceite:** pessoa não técnica executa o fluxo permitido pelo seu papel sem acessar APIs manualmente.

## Fase 6 — upload retomável ao Drive

**Estado:** PLANEJADO.

- conta e pasta isolada com escopo `drive.file`;
- estrutura por cliente, projeto e data;
- sessão retomável e checkpoint SQLite;
- envio direto do agente;
- pausa, retomada e cancelamento;
- confirmação de bytes, identificador, tamanho e integridade;
- objeto do Drive e sincronização do catálogo;
- tratamento de internet, dispositivo e limite de 5 TB.

**Aceite:** backend não transporta o binário, repetição não duplica upload e disponibilidade exige confirmação consistente.

## Fase 7 — tempo real e reconciliação

**Estado:** PLANEJADO.

- WebSocket como aviso e polling como fallback;
- presença, progresso e reconexão;
- reconciliação SQLite, PostgreSQL e Drive;
- disponibilidade, divergências, auditoria e alertas.

**Aceite:** perda do WebSocket não perde comandos e arquivos reaparecidos são reconciliados pela identidade.

## Fase 8 — fechamento do MVP

**Estado:** PLANEJADO.

- E2E no Windows;
- streaming, interrupção, retomada e desconexão;
- isolamento e segurança;
- backup e restauração;
- Docker, manual, limitações e release.

**Aceite:** fluxo completo funciona sem perda, sobrescrita ou exclusão definitiva e ações críticas ficam auditadas.

## Protocolo contínuo

Para cada incremento:

1. confirmar o estado real;
2. detalhar escopo, arquivos, riscos e aceite;
3. implementar em diff pequeno;
4. mostrar e explicar o diff;
5. executar validações proporcionais;
6. atualizar roadmap, checklist, estado e testes;
7. registrar pendências;
8. planejar o incremento seguinte.

Estados: `PLANEJADO`, `EM IMPLEMENTAÇÃO`, `IMPLEMENTADO — AGUARDA VALIDAÇÃO`, `VALIDADO` e `BLOQUEADO`.
