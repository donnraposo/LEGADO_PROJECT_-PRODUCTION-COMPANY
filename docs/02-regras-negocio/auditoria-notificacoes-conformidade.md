# Auditoria, notificações e conformidade

Rastreabilidade, alertas, termos de uso e proteção dos dados de auditoria.

> Origem: documento mestre v0.12. As numerações originais foram mantidas para rastreabilidade.

## 32. Logs e auditoria

### Auditoria funcional

Deverá registrar, entre outras ações:

- criação de conta e empresa;
- convites e alterações de papel;
- login, logout, bloqueio e recuperação;
- troca de empresa ativa;
- criação e alteração de cliente e projeto;
- análise e organização;
- arquivos movidos;
- início, pausa, retomada e cancelamento;
- agendamentos;
- uploads e verificações;
- edições e renomeações;
- downloads;
- lixeira e restauração;
- aprovações e recusas;
- mudanças de permissões;
- conexão ou falha de conta do Drive;
- alterações externas.

Cada evento deverá conter, quando aplicável:

- empresa;
- usuário;
- máquina;
- data e hora;
- ação;
- recurso;
- estado anterior e posterior;
- resultado;
- endereço de origem;
- identificador de rastreamento.

### Acesso

- somente Proprietários consultam a auditoria completa;
- Administradores veem apenas o andamento e os erros necessários às próprias operações.

### Retenção

- auditoria funcional será preservada permanentemente;
- logs técnicos antigos poderão ser arquivados;
- períodos técnicos serão definidos posteriormente.

### Sigilo

Nunca registrar:

- senhas;
- tokens completos;
- credenciais OAuth;
- segredos;
- conteúdo dos arquivos.

---


## 33. Alertas e notificações

Proprietários receberão alertas no frontend e por e-mail para eventos relevantes, incluindo:

- substituição pendente;
- alteração externa no Drive;
- falha de integridade;
- dispositivo desconectado;
- comportamento suspeito;
- conta do Drive desconectada;
- Drive sem espaço;
- falha crítica de upload;
- projeto arquivado;
- usuário bloqueado.

Administradores verão estados e erros relacionados às próprias operações e projetos autorizados.

---


### Notificações

- serão imediatos os alertas de substituição pendente, falha de integridade, Drive sem espaço ou desconectado, comportamento suspeito, bloqueio de usuário e alteração externa relevante;
- progresso, pausas comuns, conclusões, falhas recuperáveis e eventos informativos poderão compor resumo diário;
- Proprietários poderão configurar e-mails não críticos, mas não poderão desativar alertas críticos;
- alertas críticos exigirão confirmação de leitura no frontend e permanecerão destacados até o reconhecimento;
- aprovação pendente terá aviso imediato, lembrete após 24 horas e último lembrete seis horas antes da expiração;
- Administradores receberão somente notificações das próprias tarefas e dos projetos autorizados;
- entregas, falhas e confirmações de leitura serão auditadas.


### Termos e conformidade

- Termos de Uso e Política de Privacidade serão aceitos no cadastro, com versão, data, usuário e evidência do aceite;
- alterações materiais exigirão novo aceite antes da continuidade do uso;
- a empresa declarará possuir os direitos e a base legal necessários para os arquivos enviados;
- a plataforma não adquirirá propriedade sobre os arquivos;
- em regra, a empresa usuária será controladora dos dados presentes nos arquivos e a plataforma atuará como operadora, conforme o contexto e o contrato;
- haverá canal para exercício dos direitos dos titulares;
- encerrada a conta, dados operacionais pessoais serão eliminados ou anonimizados após 30 dias, salvo obrigação legal ou exercício regular de direitos;
- o lastro de auditoria será preservado com identificadores pessoais criptografados e ocultos;
- acesso à identidade dependerá de procedimento autorizado, restrito e auditado;
- criptografia não será considerada anonimização enquanto a identidade puder ser recuperada;
- dados serão mantidos somente enquanto houver finalidade e base legal;
- prazos jurídicos de retenção serão validados por especialista antes da produção;
- incidentes de segurança terão avaliação, contenção, registro e comunicação conforme a legislação aplicável.

---


