# Continuidade do MVP

**Atualizado em:** 21 de agosto de 2026.

Documento operacional para qualquer pessoa ou IA retomar o projeto sem depender do
histórico de conversas. Regras de negócio e decisões arquiteturais continuam nos
documentos temáticos; este arquivo indica o estado concreto e o próximo ponto de
trabalho.

## Local e fontes de verdade

- projeto oficial: `D:\PROJETOS\LEGADO`;
- não utilizar referências antigas a `E:\Projetos`;
- execução do MVP: [Roadmap do MVP](roadmap-mvp.md);
- itens objetivos: [Checklist do MVP](checklist-mvp.md);
- inventário técnico: [Estado da implementação](estado-implementacao.md);
- evidências: [Plano de testes](plano-testes.md);
- decisões vigentes: [Registro de decisões](../decisoes/registro-decisoes.md).

O worktree contém alterações ainda não commitadas das fases implementadas. Elas fazem
parte do projeto atual. Não executar `git reset`, descarte, limpeza ou sobrescrita para
retornar ao último commit.

## Estado resumido

| Fase | Estado | Evidência principal |
|---|---|---|
| 0 — estabilização | VALIDADO | Docker, migrations, saúde, Ruff e baseline aprovados |
| 1 — catálogo | VALIDADO | catálogo, tags, histórico, filtros, reconciliação e 55 testes backend |
| 2 — agente mínimo | IMPLEMENTADO — AGUARDA VALIDAÇÃO | SQLite, OIDC/PKCE, heartbeat, comandos e fila |
| 3 — análise e prévia | IMPLEMENTADO — AGUARDA VALIDAÇÃO | análise somente leitura, SHA-256, conflitos, prévia e 17 testes agente |
| 4 — organização segura | IMPLEMENTADO — AGUARDA VALIDAÇÃO | movimentação, checkpoints, catálogo e abertura contextual implementados; falta ensaio funcional |
| 5 — frontend web | EM IMPLEMENTAÇÃO | primeira fatia Docker com autenticação, contexto, catálogo, edição e tags |
| 6 — Drive | PLANEJADO | não iniciado |
| 7 — tempo real | PLANEJADO | não iniciado |
| 8 — fechamento | PLANEJADO | não iniciado |

## Software disponível

### Backend

- identidade OIDC e projeção local de usuário;
- empresas, convites, membros e papéis;
- clientes, projetos e acessos;
- auditoria imutável e notificações por e-mail;
- catálogo, versões físicas, tags, histórico e filtros;
- máquinas, presença, comandos persistidos e reconciliação;
- contrato OpenAPI 3.1 e infraestrutura Docker local.

### Agente local

- Python 3.14 como requisito oficial e PySide6;
- UUID persistente da instalação e SQLite migrável;
- token OIDC somente em memória;
- heartbeat, polling e ciclo de comandos;
- seleção autenticada de empresa, cliente e projeto;
- criação de empresa, cliente e múltiplos projetos pelos fluxos oficiais da API;
- registro automático da máquina após seleção da empresa;
- botão `Tentar novamente` exibido somente se o registro da máquina falhar;
- tarefas HTTP retidas até a entrega do resultado à interface Qt;
- seleção de arquivos e pastas;
- exclusão de itens técnicos, temporários, links e junções;
- metadados básicos e data do sistema de arquivos;
- SHA-256 em streaming de 4 MiB;
- duplicidades e conflitos de destino;
- prévia selecionável, cancelável e recuperável após reinício;
- destino escolhido antes da análise e confirmação explícita antes da organização;
- resolução explícita de conflitos e duplicidades;
- movimentação sem sobrescrita, com verificação SHA-256 entre volumes;
- checkpoint por arquivo, interrupção e retomada sem mover novamente;
- ingestão idempotente no catálogo sem transmitir caminhos locais.

## Validações registradas

### Backend — última baseline

- 57 testes aprovados;
- Ruff aprovado;
- migrations aplicadas e sem mudanças pendentes;
- OpenAPI 3.1 válido, com avisos documentais não bloqueadores;
- PostgreSQL, Redis, backend, Celery e Mailpit validados;
- saúde `live` e `ready` aprovada.

### Agente — última baseline

- 31 testes aprovados;
- Ruff aprovado;
- SQLite v1→v3 validado sem perder o identificador da instalação;
- conteúdo e horário dos arquivos de origem preservados;
- cancelamento e recuperação da prévia validados;
- limites arquiteturais validados;
- testes executados no runtime auxiliar Python 3.12.
- 6 testes backend das coleções de empresas, clientes e projetos aprovados.
- login OIDC e criação real de empresa chegaram ao backend com HTTP `201`;
- o ensaio revelou perda do retorno assíncrono na interface; a tarefa passou a ser
  retida até o sinal final e a regressão foi coberta automaticamente;
- o instalador `0.1.1` existente antecede as correções assíncronas e de conexão
  automática; usar o código-fonte até uma recompilação explicitamente autorizada.

### Frontend — primeira baseline

- 4 testes aprovados;
- checagem TypeScript e build Vite aprovados;
- imagem Docker construída e composição validada;
- frontend e proxy do backend responderam HTTP `200`;
- paleta principal verde, branca e preta aplicada.

## Validações ainda pendentes

- executar o agente no Python 3.14 oficial;
- subir Keycloak e testar login OIDC real no navegador;
- criar conta e empresa de teste;
- validar presença e comando `PING` ponta a ponta;
- ensaiar seleção, cancelamento e recuperação pela interface visível;
- validar a extração avançada da data original de câmera quando houver adaptador.
- ensaiar organização real em mesmo volume, entre volumes e após desconexão;
- validar login, seleção contextual, catálogo, edição e tags com dados reais;
- validar visualmente responsividade e acessibilidade do frontend.

## Próxima implementação

Preservar as pendências de validação e iniciar a fundação da Fase 6:

1. revalidar pela interface a conclusão da criação e a conexão automática da máquina;
2. implementar contratos de armazenamento e adaptador local simulado do Drive;
3. modelar conta, lote, item, tentativa e checkpoint de upload;
4. manter o binário fora do backend e preparar sessão retomável direta agente–Drive;
5. implementar detecção automática de discos externos no agente;
6. validar visualmente o fluxo completo no Windows/Python 3.14;
7. recompilar o instalador somente após nova autorização e validação do código-fonte.

## Critérios obrigatórios da Fase 4

- nenhum arquivo pode ser apagado ou sobrescrito;
- a origem não pode ser alterada antes da confirmação;
- uma repetição não pode refazer movimentação concluída;
- conflitos não podem ser resolvidos silenciosamente;
- checkpoints locais não podem conter tokens ou credenciais;
- desconexão deve interromper novas movimentações;
- testes devem usar arquivos temporários e verificar conteúdo e destino;
- roadmap, checklist, estado e testes devem ser atualizados com o diff explicado.

## Ordem de leitura para retomada

1. este documento;
2. [Roadmap do MVP](roadmap-mvp.md);
3. [Checklist do MVP](checklist-mvp.md);
4. [Organização local](../02-regras-negocio/organizacao-local.md);
5. [Filas, retomada e idempotência](../03-arquitetura/filas-retomada-idempotencia.md);
6. código e testes existentes em `agent/`;
7. continuar a Fase 5 a partir da primeira fatia executável.
