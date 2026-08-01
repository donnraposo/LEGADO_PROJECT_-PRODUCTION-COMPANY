# Downloads e lixeira

Disponibilidade, restauração, conflitos externos, confirmações e concorrência.

> Origem: documento mestre v0.12. As numerações originais foram mantidas para rastreabilidade.

## 27. Downloads

- Proprietários e Administradores autorizados poderão baixar;
- Administradores somente poderão baixar arquivos de projetos permitidos;
- haverá download individual;
- haverá seleção e download em lote;
- o usuário poderá preservar a estrutura `Cliente/Projeto/Ano/Mês/Dia`;
- poderá solicitar pacote ZIP;
- grandes volumes deverão apresentar tamanho total e alerta;
- a estratégia técnica para ZIPs muito grandes será decidida na fase técnica;
- o backend não deverá armazenar permanentemente os binários baixados.

Cada download será auditado.

---


## 28. Lixeira, restauração e exclusão

### Envio à lixeira

- Administradores autorizados poderão enviar arquivos à lixeira;
- confirmação explícita será sempre exigida;
- Drive deverá confirmar a operação;
- catálogo usará exclusão lógica;
- item ficará oculto das listagens normais;
- auditoria será preservada;
- falha no Drive impede que o catálogo considere a exclusão concluída.

### Restauração

- somente Proprietários poderão restaurar;
- restauração também exigirá confirmação;
- Drive e catálogo deverão ser reconciliados;
- histórico anterior será preservado.

### Proibição absoluta

O sistema nunca deverá:

- esvaziar automaticamente a lixeira;
- excluir definitivamente arquivos no Drive;
- excluir arquivos da estação física.

---


## 29. Alterações externas no Drive

Quando alguém alterar, mover ou excluir um arquivo diretamente no Drive:

1. sistema detecta a divergência;
2. catálogo recebe um estado correspondente;
3. frontend mostra a disponibilidade;
4. Proprietários recebem alerta no sistema e por e-mail;
5. o catálogo será sincronizado com a situação real do Drive;
6. nenhuma ação destrutiva será executada automaticamente.

Estados previstos:

```text
DISPONIVEL
INDISPONIVEL
ALTERADO_EXTERNAMENTE
MOVIDO_EXTERNAMENTE
NA_LIXEIRA
NAO_LOCALIZADO
VERIFICACAO_PENDENTE
```

---


## 30. Confirmações obrigatórias

O sistema deverá confirmar explicitamente a intenção do usuário antes de:

- mover arquivos locais;
- cancelar organização;
- iniciar upload;
- continuar após desconexão;
- substituir conteúdo no Drive;
- renomear;
- mover arquivo entre pastas do Drive;
- enviar à lixeira;
- restaurar;
- alterar cliente ou projeto quando houver impacto no Drive;
- arquivar cliente ou projeto;
- realizar ação em lote.

Confirmações em lote mostrarão quantidade, tamanho total, cliente e projeto afetados.

---


## 31. Edições simultâneas

- a primeira alteração confirmada é salva;
- o segundo usuário recebe alerta de conflito;
- a versão atual é apresentada;
- usuário poderá recarregar, cancelar ou confirmar nova alteração;
- sobrescrita de metadados exige confirmação;
- substituição do binário continua sujeita à aprovação do Proprietário.

---


### Downloads

- antes do download serão mostrados quantidade, tamanho total e espaço estimado necessário;
- ZIP único será limitado a 50 GB ou 10.000 arquivos;
- acima do limite, o conteúdo será dividido em pacotes ou baixado preservando a estrutura de pastas;
- solicitação preparada ficará disponível por 24 horas;
- links temporários expirarão em 15 minutos, serão vinculados ao usuário autenticado e poderão ser regenerados durante a validade da solicitação;
- downloads em lote poderão ser pausados, retomados e cancelados;
- a retomada preservará arquivos concluídos e continuará arquivos parciais quando tecnicamente possível;
- cancelamento não excluirá arquivos já baixados na máquina do usuário;
- falhas registrarão usuário, arquivos afetados, progresso, motivo, tentativas e resultado;
- download incompleto nunca será marcado como concluído.


