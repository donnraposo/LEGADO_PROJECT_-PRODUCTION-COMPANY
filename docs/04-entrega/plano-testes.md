# Plano de testes

**Estado:** pendente de detalhamento após a aprovação da estrutura do repositório e dos módulos.

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

Consulte também [Critérios de aceite](criterios-aceite.md) e [Requisitos não funcionais](../01-produto/requisitos-nao-funcionais.md).
