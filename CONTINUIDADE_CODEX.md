# Continuidade após reinstalação do Codex

> Este arquivo preserva somente o histórico da reinstalação do Codex. Para continuar
> o software e o MVP, leia [Continuidade do MVP](docs/04-entrega/continuidade-mvp.md).

Data do registro: 01/08/2026

## Objetivo

Reinstalar o Codex no disco `D:` sem perder os projetos nem o contexto necessário para continuar o trabalho.

## Estado atual

- Projeto definitivo: `D:\PROJETOS\LEGADO`
- Os arquivos deste projeto permanecem no disco `D:` e não dependem da instalação no `C:`.
- Dados locais do Codex encontrados em: `C:\Users\oDOnRaposo\.codex`
- Tamanho aproximado desses dados na inspeção: `0,87 GB`
- A instalação não foi identificada como pacote da Microsoft Store.
- Nenhuma pasta foi movida ou apagada até este registro.

## Contexto da conversa

Foi solicitada a transferência do Codex e/ou de seus dados do disco `C:` para o disco `D:`. A recomendação apresentada foi:

1. Manter os projetos em uma pasta independente, como `D:\Projetos`.
2. Mover os dados locais do Codex para `D:\CodexData\.codex`.
3. Preservar inicialmente a pasta original como cópia de segurança.
4. Se necessário, criar uma junção no endereço antigo para manter compatibilidade.
5. Validar login, histórico, configurações e acesso aos projetos antes de excluir qualquer cópia.

## Antes de reinstalar

1. Fechar completamente o Codex.
2. Fazer uma cópia integral de `C:\Users\oDOnRaposo\.codex` para um local seguro no disco `D:`.
3. Confirmar que esta pasta do projeto, incluindo este arquivo, está preservada.
4. Não publicar nem compartilhar a cópia de `.codex`, pois ela pode conter dados de autenticação e histórico local.

## Como retomar

Após reinstalar o Codex:

1. Abrir a pasta `D:\PROJETOS\LEGADO` no Codex.
2. Pedir: **Leia `CONTINUIDADE_CODEX.md` e continue a migração a partir do estado registrado.**
3. Restaurar os dados de `.codex` somente com o Codex fechado.
4. Validar o funcionamento antes de remover a cópia de segurança.

## Critérios de conclusão da migração

- O Codex abre normalmente a partir da nova instalação.
- O projeto `D:\PROJETOS\LEGADO` permanece íntegro.
- Login, configurações e histórico disponíveis, quando suportados pela reinstalação.
- Novos projetos podem ser armazenados no disco `D:`.
- A cópia antiga só é removida depois da validação.
