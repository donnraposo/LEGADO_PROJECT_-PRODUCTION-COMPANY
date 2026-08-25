# Uploads, aprovações e Drive

**Produto:** Gerenciador de Áudio Visual.

Estados, controles, retomada, integridade, contas e conflitos de upload.

> Origem: documento mestre v0.12. As numerações originais foram mantidas para rastreabilidade.

## 19. Upload

### Caminho do binário

Para arquivos grandes:

```text
Agente local → upload retomável → Google Drive
```

Backend e n8n controlarão autorização, pastas, eventos, metadados e estados, mas não transportarão normalmente o binário.

### Estados principais

```text
DESCOBERTO
→ ANALISADO
→ AGUARDANDO_CONFIRMACAO
→ ORGANIZANDO
→ ORGANIZADO
→ AGUARDANDO_UPLOAD
→ ENVIANDO
→ VERIFICANDO
→ SINCRONIZADO
```

Estados excepcionais:

```text
CONFLITO
INTERROMPIDO
AGUARDANDO_INTERNET
DISPOSITIVO_DESCONECTADO
FALHA_DE_INTEGRIDADE
AGUARDANDO_INTERVENCAO
CANCELADO
```

### Controles

O usuário poderá:

- pausar, retomar ou cancelar arquivo individual;
- pausar, retomar ou cancelar lote;
- alterar opcionalmente a ordem;
- definir prioridades;
- iniciar imediatamente;
- agendar data e hora;
- cancelar ou alterar agendamento.

Não haverá controle manual de velocidade nesta fase.

O mesmo arquivo não poderá participar de duas filas ativas simultaneamente.

Cada lote ficará vinculado à conta Google ativa no momento de sua criação. Trocar a
conta não moverá arquivos existentes nem retomará na nova conta uma sessão iniciada
na anterior. Arquivos ainda não iniciados exigirão novo direcionamento explícito.

### Agendamento

No horário agendado, o upload somente começará se:

- usuário ainda possuir acesso;
- sessão e autorização forem válidas;
- máquina estiver conectada;
- dispositivo e arquivo estiverem disponíveis;
- arquivo continuar íntegro;
- Drive estiver disponível.

Caso contrário, ficará aguardando a condição necessária ou nova confirmação.

---


## 20. Pausa, retomada e cancelamento

### Falha temporária

O sistema fará três tentativas automáticas com intervalos progressivos. Antes de retomar, deverá consultar o ponto confirmado pelo Drive.

Depois da terceira falha:

- tarefa muda para `AGUARDANDO_INTERVENCAO`;
- usuário poderá tentar novamente;
- falhas críticas serão notificadas aos Proprietários.

### Dispositivo desconectado durante upload

1. upload é pausado;
2. desconexão é registrada;
3. usuário reconecta o dispositivo;
4. agente verifica identidade, caminho, tamanho e checksum;
5. progresso confirmado é mostrado;
6. usuário confirma explicitamente;
7. upload continua.

Outro arquivo com o mesmo nome nunca será aceito automaticamente como substituto.

### Logout, bloqueio ou perda de acesso

- upload pausa no próximo bloco seguro;
- novos comandos são bloqueados;
- retomada exige login e confirmação;
- arquivos locais permanecem intactos.

### Cancelamento

- sessão incompleta será encerrada quando possível;
- conteúdo incompleto não será exibido como disponível;
- metadado provisório será marcado como cancelado;
- arquivo local permanecerá inalterado;
- auditoria será preservada.

---


## 21. Integridade e atomicidade

Um arquivo somente será considerado sincronizado quando:

- upload estiver concluído;
- Drive retornar um identificador;
- tamanho estiver confirmado;
- checksum for comparado quando disponível;
- metadados forem persistidos;
- operação tiver resultado consistente.

Regras:

- checksum local será calculado antes ou durante o envio;
- alteração local durante o upload invalida a tarefa;
- tentativas devem evitar arquivos duplicados;
- arquivo incompleto nunca será mostrado como sincronizado;
- falha de integridade não altera o arquivo local;
- falha crítica gera alerta.

---


## 22. Google Drive e contas

- Google Workspace será obrigatório para o armazenamento principal;
- inicialmente haverá um Drive Compartilhado central da produtora;
- os arquivos pertencerão à organização, e não a uma pessoa individual;
- ela não será compartilhada diretamente com empresas ou usuários externos;
- o sistema deverá permitir adicionar outras contas no futuro;
- credenciais nunca serão expostas no frontend;
- cada cliente ou projeto poderá futuramente ser associado a uma conta configurada;
- criação de pastas ocorrerá apenas quando necessária.
- o sistema gerenciará somente arquivos enviados pela própria aplicação;
- arquivos desconhecidos adicionados diretamente ao Drive não serão importados automaticamente para o catálogo;
- o escopo OAuth inicial será `drive.file`;
- arquivos acima de 5 TB continuarão organizados e catalogados localmente, mas receberão o estado `NAO_SUPORTADO_PELO_DRIVE`;
- a limitação diária de upload da conta será monitorada e poderá pausar tarefas em `AGUARDANDO_COTA_DRIVE`.

### Drive sem espaço

- upload será pausado;
- arquivos locais permanecerão intactos;
- Proprietários serão avisados no sistema e por e-mail;
- Administradores verão o estado da tarefa;
- retomada dependerá de espaço ou de outra conta configurada e de nova validação.

---


## 23. Conflitos no Drive

O Drive permite arquivos diferentes com o mesmo nome. O conflito deverá considerar:

- pasta;
- nome;
- tamanho;
- checksum;
- identificador do Drive.

O alerta mostrará arquivo local e arquivo existente.

Opções:

1. cancelar;
2. renomear o novo arquivo;
3. solicitar substituição do conteúdo existente.

Renomear será a alternativa segura sugerida. Substituir conteúdo solicitado por Administrador dependerá de aprovação de Proprietário.

### Aprovação de substituição

- solicitação fica pendente;
- Proprietários recebem alerta interno e por e-mail;
- qualquer Proprietário autorizado poderá aprovar ou recusar;
- solicitação expira em 48 horas;
- expiração cancela a operação;
- nada é substituído antes da aprovação;
- a decisão fica auditada.

---


### Upload e aprovação

- solicitação de substituição expirada após 48 horas será cancelada sem alterar o arquivo existente;
- o Administrador poderá criar nova solicitação, sujeita a nova validação e aprovação;
- upload agendado sem sessão válida não começará e ficará `AGUARDANDO_AUTENTICACAO`;
- após novo login, o usuário deverá confirmar o reagendamento;
- cada lote terá no máximo 10.000 arquivos, sem limite funcional fixo de tamanho total;
- seleções maiores serão divididas em lotes;
- durante indisponibilidade prolongada do Drive, tarefas permanecerão pausadas sem perda de progresso;
- Proprietários receberão alerta imediato e atualizações periódicas;
- o Proprietário definirá a conta padrão do Drive e poderá associar contas específicas a clientes ou projetos;
- arquivo local alterado depois da sincronização será marcado como divergente;
- não haverá reenvio ou substituição automática;
- Administrador poderá solicitar novo envio, e substituição continuará dependendo de Proprietário.


