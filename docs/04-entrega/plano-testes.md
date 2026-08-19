# Plano de testes

> A ordem de validação da primeira entrega é acompanhada no [Checklist do MVP](checklist-mvp.md).

**Baseline de 3 de agosto de 2026:** 42 testes aprovados, Ruff aprovado, migrations consistentes e OpenAPI sem erros.

**Baseline de 18 de agosto de 2026:** imagens reconstruídas; serviços centrais e Celery Beat operacionais; saúde `live` e `ready` aprovada; 42 testes aprovados; Ruff e migrations aprovados; OpenAPI válido com 19 avisos documentais não bloqueadores.

**Incremento de reconciliação do catálogo em 18 de agosto de 2026:** 51 testes aprovados; transições válidas e inválidas, repetição idempotente, concorrência otimista, vínculo de máquina, isolamento empresarial e auditoria cobertos; migration e OpenAPI aprovados.

**Fechamento da Fase 1 em 18 de agosto de 2026:** 55 testes aprovados; auditoria idempotente de tags, tags nas respostas, histórico paginado, restauração exclusiva de Proprietários, concorrência e filtros combinados cobertos; Ruff, migrations, OpenAPI e saúde aprovados.

**Incremento da Fase 2 em 19 de agosto de 2026:** 7 testes do agente aprovados no
runtime auxiliar Python 3.12; Ruff aprovado; identificação e fila sobrevivem ao
reinício do repositório; banco não contém campos de token ou senha; PKCE segue o vetor
RFC; heartbeat e transições `ACKNOWLEDGED → RUNNING → SUCCEEDED` foram cobertos;
contrato HTTP e inicialização/encerramento da tela Qt foram validados. O JSON do realm
e a composição Docker são válidos. Pendente ensaio manual com Python 3.14 e Keycloak.

**Incremento da Fase 3 em 19 de agosto de 2026:** suíte do agente ampliada para 17
testes; varredura técnica, destino Windows, SHA-256 em blocos, preservação da origem,
duplicidade, conflito de nome, cancelamento, prévia recuperável, seleção persistente,
upgrade SQLite v1→v2 e limites arquiteturais cobertos. Ruff aprovado. Pendente ensaio
manual da interface em Python 3.14 e provedor avançado de metadados de câmera.

**Incremento da Fase 4 em 19 de agosto de 2026:** suíte do agente ampliada para 25
testes; confirmação, alteração da origem, destino existente, movimentação no mesmo
volume, cópia verificada entre volumes, preservação de temporário preexistente,
checkpoint, recuperação de queda, ingestão no catálogo e retomada após indisponibilidade
foram cobertos. Ruff do agente e backend e três testes arquiteturais do backend foram
aprovados. Os dois novos testes de integração Django, migration PostgreSQL e ensaio
visual em Windows aguardam o ambiente Docker/Python 3.14.

**Estado:** EM EXECUÇÃO. Baselines do backend e do agente registradas até 19 de agosto
de 2026; próximas validações são os ensaios funcionais das Fases 2 e 3 e os testes de
segurança da organização local na Fase 4.

Os testes deverão cobrir, no mínimo, regras de domínio, isolamento entre empresas, contratos de API, idempotência, retomada de upload, integração com Drive, segurança, auditoria e fluxos ponta a ponta.

## Cobertura incremental atual

- normalização de nomes de clientes e projetos;
- criação dentro da empresa ativa;
- acesso automático do Administrador ao projeto criado;
- negação para usuário sem vínculo empresarial;
- bloqueio do uso de cliente pertencente a outra empresa.
- aceite único de convite vinculado ao e-mail autenticado;
- rejeição do convite por conta diferente;
- proteção do último Proprietário ativo;
- concessão e revogação de acesso a projetos.
- imutabilidade dos eventos de auditoria;
- registro de convites e alterações de acesso;
- composição do e-mail de convite e seu link de aceite.
- bloqueio de dependências de framework nas camadas de domínio e aplicação;
- conflito de versão de membros retornado como HTTP `409`;
- consulta de auditoria restrita a Proprietários.
- cancelamento de convite impede aceite posterior e gera auditoria.
- `change_state` contém somente campos alterados, adicionados ou removidos;
- API de auditoria expõe nome, descrição e os três estados.
- views de convite não podem importar ORM ou transações de banco.
- todos os adaptadores HTTP são verificados contra ORM e transações;
- PostgreSQL rejeita alteração e exclusão direta de eventos de auditoria;
- tentativa, entrega e falha de e-mail registram somente dados protegidos;
- fluxo Django, Redis, Celery e Mailpit validado funcionalmente.
- criação de arquivo lógico e versão física sem persistir caminho local completo;
- isolamento do catálogo por projeto para Administradores;
- alteração de metadados rejeita versão desatualizada com HTTP `409`.
- Proprietário cria e arquiva tag personalizada, sem afetar tags genéricas;
- Administrador não gerencia tags e só aplica tags em projetos permitidos.
- busca e filtros respeitam empresa, projeto, estado e tag;
- cursor inválido é rejeitado e páginas não repetem arquivos.
- heartbeat repetido não duplica máquina na mesma empresa;
- comandos preservam sequência e idempotência por empresa;
- chave idempotente com conteúdo divergente produz conflito;
- payloads com segredo, token ou caminho local são rejeitados;
- máquinas e comandos permanecem isolados entre empresas.
- confirmação e progresso exigem máquina vinculada e versão atual;
- comandos concluídos não regressam para estados de execução;
- sucesso conclui o progresso em 100% e preserva resultado não sensível.
- agente persiste instalação, vínculo empresarial e comandos de forma idempotente;
- token do agente existe somente na sessão em memória e é descartado ao fechar;
- gateway envia token, contexto empresarial, sequência e versão esperada;
- polling renova heartbeat e retoma comandos locais ainda não concluídos;
- interface Qt inicia desconectada e encerra sem preservar a autenticação.
- varredura ignora lixeira, itens técnicos, temporários, links e seleções repetidas;
- análise preserva conteúdo, tamanho e data de modificação dos arquivos de origem;
- checksum SHA-256 é calculado em blocos e detecta alteração durante a leitura;
- prévia registra origem, destino, data, tipo, tamanho, checksum, conflitos e avisos;
- cancelamento preserva itens concluídos e seleção da prévia sobrevive ao reinício;
- migration local v2 preserva a instalação criada pela v1;
- teste arquitetural bloqueia infraestrutura nas camadas de domínio e aplicação.
- destino faz parte da prévia e mudança da origem invalida a confirmação;
- destino existente e temporário técnico preexistente nunca são removidos ou substituídos;
- queda entre movimentação e checkpoint é reconciliada pelo checksum;
- falha do catálogo deixa a operação retomável e reutiliza a mesma chave idempotente;
- gateway do agente não envia `source_path` nem `destination_path` ao backend;
- backend devolve o mesmo arquivo em ingestão repetida e rejeita conteúdo divergente.

Consulte também [Critérios de aceite](criterios-aceite.md) e [Requisitos não funcionais](../01-produto/requisitos-nao-funcionais.md).
