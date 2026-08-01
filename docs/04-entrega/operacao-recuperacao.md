# Operação, backup e recuperação

**Estado:** PARCIALMENTE APROVADO em 1º de agosto de 2026.

As regras de persistência e recuperação estão aprovadas. O detalhamento executável dependerá da definição completa da infraestrutura e da hospedagem.

## Dados protegidos

- banco da aplicação, incluindo catálogo, estados, comandos e auditoria;
- banco do Keycloak;
- banco e chave de criptografia do n8n;
- papéis e permissões globais do PostgreSQL;
- configurações versionadas da infraestrutura;
- segredos e chaves em kit de recuperação separado;
- artefatos locais que não possam ser regenerados.

Redis, caches, arquivos temporários e prévias regeneráveis não serão tratados como fontes oficiais.

## Política inicial de backup

- backup lógico diário de cada banco PostgreSQL;
- backup dos papéis globais do cluster;
- backup anterior a migrations críticas;
- armazenamento criptografado com Restic ou solução equivalente aprovada;
- ao menos uma cópia fora do disco e do volume original;
- retenção inicial de 7 cópias diárias, 4 semanais e 6 mensais;
- verificação periódica de integridade;
- teste mensal de restauração;
- registro do horário, versão, tamanho, checksum e resultado de cada execução.

O backup só será considerado válido depois de uma restauração testada.

## Recuperação

Ordem padrão:

1. isolar o ambiente afetado;
2. identificar o último estado confiável;
3. preservar banco, volume e logs existentes para análise;
4. provisionar volume ou servidor limpo;
5. restaurar papéis e bancos;
6. restaurar chaves e segredos pelo canal seguro;
7. aplicar somente migrations necessárias à versão restaurada;
8. validar contagens, amostras, integridade e auditoria;
9. iniciar serviços internos;
10. executar conciliação não destrutiva com Google Drive;
11. liberar frontend e agentes;
12. registrar incidente e evidências.

Nenhuma restauração sobrescreverá automaticamente um banco existente.

## Recuperação para ponto no tempo

Na produção comercial, backup físico e WAL permitirão recuperar o cluster até antes de exclusão acidental, corrupção lógica ou migration incorreta. O ponto deverá ser validado em instância isolada antes de substituir o ambiente ativo.

## Google Drive

- arquivos originais do Drive não fazem parte do volume PostgreSQL;
- backup do catálogo não substitui backup dos binários;
- após recuperação do banco, será executada conciliação não destrutiva;
- política organizacional de retenção e backup do Drive será definida antes da operação comercial;
- nenhuma recuperação poderá excluir ou substituir automaticamente arquivos do Drive.

## Metas iniciais

| Ambiente | RPO | RTO |
|---|---:|---:|
| desenvolvimento | sem garantia | melhor esforço |
| piloto | 24 horas | 8 horas |
| produção comercial | definido por contrato futuro | definido por contrato futuro |

## Validações obrigatórias

- recriação do container com o mesmo volume;
- restauração em volume vazio;
- restauração em outra máquina;
- simulação de migration com falha;
- comparação de contagens e identificadores;
- verificação de segredos ausentes dos artefatos;
- ensaio futuro de recuperação PITR.

Consulte [Persistência, deploy e migrations](../03-arquitetura/persistencia-deploy-migracoes.md) e [Filas, retomada e idempotência](../03-arquitetura/filas-retomada-idempotencia.md).
