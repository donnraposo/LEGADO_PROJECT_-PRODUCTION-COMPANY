# Empresas, usuários e autenticação

Isolamento, papéis, sessões, máquinas e regras complementares de usuários.

> Origem: documento mestre v0.12. As numerações originais foram mantidas para rastreabilidade.

## 7. Empresas e isolamento

### Cadastro

- haverá cadastro público de conta;
- qualquer pessoa poderá criar uma empresa;
- o criador se torna Proprietário da nova empresa;
- uma conta poderá participar de várias empresas;
- ao entrar, o usuário escolherá a empresa ativa;
- uma pessoa poderá ter papéis diferentes em empresas diferentes;
- novos participantes de uma empresa entram somente por convite de um Proprietário.

### Isolamento

- dados de uma empresa nunca poderão aparecer em outra;
- clientes, projetos, arquivos, contas do Drive, logs e configurações pertencem à empresa;
- toda requisição deverá possuir empresa, usuário e permissões identificados;
- troca de empresa ativa deverá ser explícita e auditada.

---


## 8. Papéis e permissões

Existirão somente dois papéis.

### Proprietário

Poderá:

- executar todas as operações do sistema;
- visualizar todos os projetos e arquivos da empresa;
- convidar usuários;
- criar, bloquear e remover Administradores;
- promover um Administrador a Proprietário;
- transferir responsabilidades de propriedade;
- definir projetos acessíveis por Administrador;
- conectar e remover contas do Drive;
- aprovar substituição de arquivos;
- configurar o comportamento de itens arquivados;
- consultar toda a auditoria;
- restaurar arquivos enviados à lixeira;
- criar tags personalizadas;
- receber alertas internos e por e-mail.

Poderão existir vários Proprietários. Deve existir sempre pelo menos um Proprietário ativo. O último Proprietário não poderá remover sua própria função ou desativar a própria conta sem promover outra pessoa.

### Administrador

Poderá:

- acessar apenas projetos atribuídos;
- criar empresas, clientes e projetos;
- receber acesso automático ao projeto que criar;
- organizar e enviar arquivos;
- controlar as próprias filas;
- editar metadados permitidos;
- renomear arquivos no Drive;
- baixar arquivos autorizados;
- mover arquivos autorizados para a lixeira após confirmação;
- solicitar substituição de conteúdo existente.

Não poderá:

- convidar usuários;
- consultar auditoria completa;
- restaurar arquivos da lixeira;
- substituir conteúdo sem aprovação de um Proprietário;
- acessar projetos não atribuídos.

### Acesso a projetos

- Proprietários têm acesso automático a todos os projetos;
- o Proprietário define quais projetos cada Administrador pode acessar;
- o Administrador recebe acesso automático ao projeto que criar;
- remoção de acesso é imediata;
- tarefas pendentes são suspensas;
- uploads em andamento param no próximo bloco seguro;
- um Proprietário poderá reatribuir ou retomar a tarefa.

---


## 9. Autenticação e sessões

- login por e-mail e senha;
- recuperação de senha exclusivamente por e-mail;
- autenticação em dois fatores não será exigida nesta fase;
- nenhuma movimentação ou operação sobre arquivos pode ocorrer antes do login;
- uma sessão permanece válida até o logout, bloqueio ou revogação;
- o mesmo usuário não poderá manter sessões ativas simultaneamente em várias máquinas;
- um novo login concorrente deverá invalidar ou encerrar a sessão anterior;
- após reinício do computador, o agente local sempre exigirá nova autenticação;
- credenciais ou tokens locais não poderão restaurar automaticamente a sessão do agente após reinício;
- logout pausa uploads no próximo bloco seguro;
- bloqueio ou redefinição de acesso revoga sessões imediatamente;
- retomada exige novo login e confirmação.

### Operações que exigem autenticação

- analisar dispositivo ou pasta;
- gerar prévia;
- mover arquivos;
- verificar pastas organizadas;
- criar ou alterar empresa, cliente e projeto;
- iniciar ou retomar upload;
- editar, renomear, baixar, arquivar, enviar à lixeira ou restaurar.

---


## 10. Máquinas e rastreabilidade

- não haverá aprovação prévia de instalação;
- uma empresa poderá utilizar quantas máquinas forem necessárias;
- cada pessoa deverá usar seu próprio login;
- cada upload exige sessão autenticada;
- a máquina será identificada automaticamente para auditoria;
- o login determinará empresa, papel e projetos disponíveis.

Cada operação deverá registrar, quando aplicável:

- empresa;
- usuário;
- papel;
- máquina;
- sistema operacional;
- dispositivo;
- cliente e projeto;
- arquivos e tamanho total;
- início, término e interrupções;
- resultado;
- identificador de rastreamento.

---


### Empresa e usuários

- somente Proprietário poderá arquivar uma empresa;
- empresa arquivada não aceitará novas operações nem permitirá downloads;
- o arquivamento será reversível e tarefas serão pausadas no próximo ponto seguro;
- encerramento exigirá confirmação em duas etapas, ausência de tarefas ativas e definição do destino dos arquivos no Drive;
- o sistema nunca excluirá arquivos do Drive como consequência do encerramento;
- haverá prazo reversível de 30 dias antes do encerramento definitivo;
- quando um usuário sair, seus acessos e sessões serão revogados imediatamente;
- tarefas desse usuário serão pausadas e transferidas a um Proprietário;
- autoria e auditoria serão preservadas, e arquivos e projetos continuarão pertencendo à empresa;
- convites serão de uso único, válidos por sete dias e vinculados ao e-mail convidado;
- convites poderão ser cancelados ou reenviados, e o mais recente invalidará o anterior;
- senhas terão no mínimo 12 caracteres e tentativas inválidas causarão bloqueio temporário progressivo;
- novo login concorrente será aceito após aviso e encerrará a sessão anterior;
- operações da sessão anterior pararão no próximo bloco seguro e a retomada exigirá autenticação e confirmação.


