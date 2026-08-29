# Filas, retomada e idempotência

Fontes de verdade, entrega, concorrência, checkpoints e filas Celery.

> Origem: documento mestre v0.12. As numerações originais foram mantidas para rastreabilidade.

### Filas, retomada, concorrência e idempotência aprovadas



#### Fontes de verdade



- PostgreSQL será a fonte dos estados e tarefas centrais;

- SQLite será a fonte da fila e execução local do agente;

- Google Drive será a fonte da quantidade de bytes efetivamente recebida;

- Redis será somente transporte, cache e distribuição de eventos;

- identificadores do Celery não serão usados como identificadores do domínio.



#### Outbox e inbox



- alteração de domínio, auditoria e mensagem de saída serão persistidas na mesma transação PostgreSQL;

- indisponibilidade de Redis, Celery ou n8n não apagará o evento;

- mensagens pendentes serão reenviadas pela outbox;

- consumidores manterão inbox de mensagens processadas;

- entrega será considerada pelo menos uma vez, com efeitos idempotentes.



#### Identificação de comandos



Cada comando terá:



- identificador próprio;

- chave de idempotência;

- empresa;

- máquina;

- recurso;

- versão;

- número sequencial;

- identificador de correlação.



Regras:



- mesma chave e mesmos dados retornarão o resultado anterior;

- mesma chave com dados diferentes produzirá conflito;

- mensagens repetidas ou fora de ordem não poderão duplicar efeitos ou regredir estados;

- operações externas verificarão o estado atual antes de agir;

- repetição não poderá duplicar upload, movimentação, notificação crítica ou exclusão lógica.



#### Concorrência



- registros mutáveis terão número de versão para bloqueio otimista;

- transições críticas usarão transação e bloqueio PostgreSQL;

- um arquivo não poderá possuir operações ativas incompatíveis;

- pausa, cancelamento e perda de acesso serão aplicados no próximo bloco seguro;

- comandos antigos serão recusados quando a versão do recurso tiver avançado;

- a máquina responsável manterá uma concessão renovável da tarefa;

- perda da concessão suspenderá a tarefa e permitirá reatribuição autorizada.



#### Fila local



SQLite manterá:



- arquivos analisados;

- tarefas pendentes;

- trabalhos de upload e identificadores de tentativa, nunca a URL da sessão;

- último estado conhecido;

- eventos ainda não confirmados pelo backend;

- comandos já processados;

- checksum e identidade local;

- estado de pausa ou cancelamento.



Após reinício do computador, a fila será preservada, mas permanecerá bloqueada até nova autenticação.

O schema SQLite v4 usa `upload_jobs` com uma linha idempotente por `item_id`. São
persistidos caminho local, versão lógica associada, tentativa, tamanho, SHA-256,
checkpoint, estado e erro resumido. Credenciais OAuth, access token, refresh token e
URL retomável são proibidos no banco local.



#### Progresso e checkpoints



- agente poderá transmitir progresso transitório em intervalo de aproximadamente dois segundos;

- frontend consulta lotes ativos a cada dois segundos; Channels permanece planejado
  como aviso, com polling como fallback;

- PostgreSQL persistirá checkpoints periódicos, mudanças de estado e marcos relevantes de volume;

- antes de retomar, agente consultará o ponto confirmado pelo Drive;

- progresso informado pelo agente não substituirá a confirmação do Drive.

Pausa, retomada e cancelamento são mutações centrais versionadas e idempotentes. O
agente consulta o estado antes de cada bloco e confirma a aplicação no mesmo recurso.
Enquanto o controle permanecer `PAUSED`, nenhuma nova transmissão será iniciada. Toda
atualização rejeita `confirmed_bytes` inferior ao checkpoint já persistido.

O painel restaura o último `batch_id` da empresa após recarga, mas sempre consulta o
backend como fonte de verdade. O polling termina nos estados finais e o percentual é
derivado de `confirmed_bytes / total_bytes`, sem regressão local.

No transporte atual, cada resposta `308` do Drive produz checkpoint local e central.
Depois de reiniciar, o agente solicita novamente a sessão ao backend; o backend consulta
o Drive e devolve o ponto confirmado. O arquivo é reposicionado nesse byte antes do
próximo bloco, sem confiar apenas no valor SQLite.



#### Filas Celery



- `critical`: bloqueios e alertas críticos;

- `default`: tarefas comuns;

- `notifications`: e-mails e resumos;

- `reconciliation`: Drive e catálogo;

- `integrations`: comunicação com n8n;

- `maintenance`: artefatos temporários e rotinas técnicas.



#### Critérios de confiabilidade



- repetir comando produzirá no máximo um efeito;

- queda de Redis não perderá tarefa de negócio;

- queda do agente não perderá a fila local;

- mensagem fora de ordem não regredirá estado;

- upload retomado consultará o Drive;

- duas máquinas não operarão simultaneamente o mesmo arquivo;

- transições relevantes permanecerão auditadas.



