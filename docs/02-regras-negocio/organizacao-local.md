# Organização local

Seleção de dispositivos, datas, estrutura, prévia, preservação e abertura do frontend.

> Origem: documento mestre v0.12. As numerações originais foram mantidas para rastreabilidade.

## 12. Seleção do dispositivo e escopo

O usuário poderá selecionar:

- um HARD DISK inteiro pelo botão `Selecionar HD`;
- uma ou mais pastas específicas;
- arquivos específicos;
- quais arquivos serão organizados;
- quais arquivos serão enviados.

Somente uma organização poderá ser executada por vez em cada máquina.

### Itens ignorados automaticamente

- lixeira do dispositivo;
- arquivos do sistema;
- pastas técnicas protegidas;
- arquivos temporários.

### Pastas já organizadas

Ao encontrar pastas organizadas, o sistema perguntará se o usuário deseja:

- ignorá-las;
- verificar arquivos ainda não enviados;
- verificar todos os arquivos;
- selecionar manualmente arquivos para upload.

Arquivos já organizados não serão movidos novamente apenas por terem sido encontrados em uma nova análise.

---


## 13. Regra de data

Ordem de determinação:

1. data original de criação ou captura registrada pela câmera;
2. data de criação registrada pelo sistema de arquivos;
3. pasta `DATA_NAO_IDENTIFICADA`, caso nenhuma data válida exista.

Somente ano, mês e dia serão usados. Horário e fuso não farão parte da estrutura.

O sistema poderá transportar qualquer formato. A extração de metadados avançados dependerá do formato, mas um formato desconhecido não impedirá organização ou upload. Na prévia, o sistema deverá mostrar a data escolhida e sua origem.

---


## 14. Estrutura de organização

A estrutura local e a estrutura lógica do Drive serão:

Ao iniciar cada análise, o agente exige a escolha explícita da mídia ou de uma pasta no
PC onde o projeto será organizado. O último local é persistido no SQLite sem credenciais
apenas como sugestão e nunca é reutilizado sem confirmação. O destino não pode estar
dentro de uma origem selecionada. Após a escolha, o agente calcula automaticamente:

```text
Cliente/
└── Projeto/
    └── Ano/
        └── Mês/
            └── Dia/
                └── arquivo.ext
```

Exemplo:

```text
Cliente Aurora/
└── Campanha Institucional/
    └── 2026/
        └── 07/
            └── 31/
                ├── entrevista-01.mov
                ├── audio-externo.wav
                └── fotografia-01.raw
```

---


## 15. Prévia obrigatória

Nenhum arquivo poderá ser movido antes de uma prévia e confirmação.

A prévia deverá mostrar:

- origem;
- destino;
- cliente;
- projeto;
- data encontrada;
- origem da data;
- nome;
- extensão;
- tamanho;
- possíveis duplicidades;
- conflitos de nome;
- avisos de metadados ausentes.

O usuário poderá desmarcar arquivos. Arquivos desmarcados permanecerão na localização original.

---


## 16. Organização e preservação local

- arquivos serão movidos para suas pastas após confirmação;
- não poderão ser apagados definitivamente;
- após a organização, não haverá edição automática posterior;
- renomeações feitas no frontend afetarão somente o Drive;
- upload, cancelamento ou falha não alterarão o arquivo local;
- após upload concluído, o arquivo local não será movido, renomeado ou apagado;
- o catálogo apenas o marcará como enviado.

### Desconexão durante a organização

Se o dispositivo for desconectado:

1. organização é interrompida;
2. nenhuma movimentação nova ocorre;
3. o usuário deverá reiniciar a organização;
4. o agente fará nova análise completa;
5. arquivos já movidos serão reconciliados;
6. uma nova prévia será apresentada;
7. nova confirmação será obrigatória.

Reiniciar não significa repetir cegamente os movimentos já realizados.

---


## 17. Conflitos e duplicidades locais

### Mesmo nome e destino

O sistema deverá alertar o usuário responsável. Como arquivos físicos não podem ser eliminados, as opções locais serão:

- renomear automaticamente;
- informar outro nome;
- ignorar o arquivo;
- cancelar a organização.

Não haverá sobrescrita destrutiva no dispositivo físico.

### Mesmo conteúdo

Se arquivos tiverem o mesmo checksum, o sistema perguntará ao usuário. Opções:

- manter ambos;
- ignorar o novo;
- cancelar para análise manual.

Nenhuma decisão será tomada silenciosamente.

---


## 18. Abertura do frontend

Depois da organização, o agente abrirá o frontend online diretamente na área de upload relacionada à operação autenticada.

O frontend mostrará os arquivos organizados e permitirá:

- adicionar ou retirar arquivos da fila;
- selecionar arquivos;
- editar campos permitidos;
- iniciar, pausar, retomar e cancelar;
- agendar;
- acompanhar progresso;
- consultar arquivos disponíveis no Drive;
- renomear, baixar e enviar à lixeira conforme as permissões.

O frontend não acessará diretamente o disco. O agente local fará esse acesso de forma controlada.

---


