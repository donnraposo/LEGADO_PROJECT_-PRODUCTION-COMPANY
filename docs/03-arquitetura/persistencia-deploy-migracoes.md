# Persistência, deploy e migrations

**Estado:** APROVADO em 1º de agosto de 2026.

## Objetivo

Preservar metadados, estados, auditoria e credenciais protegidas durante atualizações, falhas de containers, migrations e recuperação de infraestrutura.

## Separação obrigatória

- containers serão substituíveis;
- dados PostgreSQL permanecerão em volume persistente externo;
- imagens não conterão dados de execução;
- PostgreSQL, Keycloak e n8n usarão bancos e usuários separados, ainda que compartilhem inicialmente o mesmo cluster;
- Redis continuará sendo transporte e cache, nunca fonte oficial de dados;
- chaves de criptografia não ficarão no banco, no volume PostgreSQL ou no repositório.

## Volumes

- cada ambiente terá nome de volume explícito e estável;
- piloto e produção usarão volume previamente provisionado e declarado como externo;
- mudança do nome do projeto Compose não poderá redirecionar o banco para outro volume;
- a esteira validará a identidade do banco antes de migrations;
- volume ausente, vazio ou inesperado bloqueará a implantação;
- a aplicação nunca inicializará silenciosamente um novo banco em ambiente persistente;
- parar, remover ou recriar um container não removerá seus dados.

São proibidos na esteira normal:

- `docker compose down -v`;
- `docker volume prune`;
- remoção automática do volume PostgreSQL;
- alteração automática do nome do volume;
- montagem do diretório de dados de uma versão principal incompatível do PostgreSQL.

## Esteira de atualização

1. construir imagem imutável e identificada pela versão;
2. executar testes de domínio, integração, arquitetura e migrations;
3. verificar banco, volume, espaço, backup e versão PostgreSQL;
4. criar backup anterior à implantação quando houver mudança de esquema ou dados;
5. criar ponto de restauração quando houver WAL/PITR disponível;
6. aplicar migrations em tarefa única, protegida contra execução concorrente;
7. iniciar os novos containers da aplicação;
8. validar vida, prontidão, versão da aplicação e versão do esquema;
9. liberar tráfego somente depois das verificações;
10. manter a imagem anterior disponível para rollback.

Falha em qualquer verificação interromperá a publicação. A esteira não tentará corrigir ou apagar dados automaticamente.

## Migrations

Será usado o padrão `expandir → migrar → contrair`:

1. adicionar estrutura compatível sem remover a anterior;
2. publicar código capaz de trabalhar durante a transição;
3. migrar e validar dados em lotes idempotentes;
4. tornar a nova estrutura obrigatória somente após a migração;
5. remover a estrutura antiga em publicação posterior.

Regras:

- migrations de esquema e grandes transformações de dados serão separadas;
- alterações extensas serão executadas em lotes com checkpoints;
- migrations deverão possuir estratégia de avanço, validação e recuperação;
- operações destrutivas exigirão aprovação específica e backup verificado;
- índices grandes deverão ser criados sem bloqueio prolongado quando suportado;
- somente uma instância poderá aplicar migrations por vez;
- aplicação nova e anterior deverão permanecer compatíveis durante a janela de publicação;
- rollback automático reverterá a aplicação, não modificará dados às cegas.

## Atualização do PostgreSQL

- imagens serão fixadas em uma versão suportada, nunca em `latest`;
- atualização de versão secundária será testada e precedida por backup;
- atualização de versão principal terá procedimento próprio;
- mudança principal exigirá `pg_upgrade`, replicação lógica ou exportação e restauração;
- volume antigo permanecerá preservado até validação completa;
- compatibilidade de extensões e checksums será verificada antes da mudança.

## Recuperação por cenário

| Evento | Resposta |
|---|---|
| atualização da aplicação | reconectar ao mesmo banco e volume |
| perda do container PostgreSQL | recriar container e remontar o volume |
| falha da nova aplicação | retornar à imagem anterior compatível |
| falha de migration | interromper implantação e preservar estado |
| volume não encontrado | bloquear ambiente e alertar responsável |
| perda do disco | restaurar backup em novo volume |
| alteração indevida de dados | recuperar para ponto anterior validado |
| perda do servidor | recriar infraestrutura e restaurar dados e segredos |

Restauração não será executada automaticamente sobre um banco existente. Em alta disponibilidade futura, failover para réplica saudável poderá ser automático; restauração destrutiva continuará controlada.

## Proteção dos metadados

- criptografia do disco ou volume no ambiente hospedado;
- TLS nas conexões fora do host confiável;
- backups criptografados;
- dados pessoais sensíveis criptografados por campo quando definido pelo modelo;
- índice HMAC separado para buscas exatas, como por e-mail;
- chaves versionadas e armazenadas fora dos dados;
- tokens, URLs de sessão, segredos e dados pessoais não aparecerão em logs;
- trilha de auditoria permanecerá independente dos logs técnicos.

## Evolução da disponibilidade

### Fase inicial

- uma instância PostgreSQL;
- volume persistente;
- backup lógico diário e anterior a mudanças críticas;
- restauração testada;
- meta inicial de RPO de 24 horas e RTO de 8 horas para o piloto.

### Produção comercial futura

- PostgreSQL gerenciado ou cluster dedicado;
- réplica em servidor ou zona diferente;
- backup físico e arquivamento contínuo de WAL;
- recuperação para ponto no tempo;
- failover monitorado;
- RPO e RTO revistos conforme contrato e orçamento.

Réplica não substitui backup. Alta disponibilidade autogerenciada não será simulada com vários containers no mesmo servidor.

## Critérios de aceite

- recriar o container preserva integralmente os dados;
- volume ausente nunca resulta em banco vazio aceito como válido;
- migrations concorrentes são impedidas;
- falha de implantação não altera dados fora da migration autorizada;
- restauração funciona em volume e máquina vazios;
- contagens, identificadores e integridade são verificados depois da restauração;
- atualização principal do PostgreSQL possui ensaio e rollback próprios;
- nenhum segredo aparece em imagem, Git, log ou backup não criptografado.

## Referências

- [Volumes Docker](https://docs.docker.com/engine/storage/volumes/)
- [Migrations de dados no Django](https://docs.djangoproject.com/en/6.0/howto/writing-migrations/)
- [Arquivamento contínuo e PITR no PostgreSQL](https://www.postgresql.org/docs/18/continuous-archiving.html)
- [Atualização de clusters PostgreSQL](https://www.postgresql.org/docs/16/upgrading.html)
