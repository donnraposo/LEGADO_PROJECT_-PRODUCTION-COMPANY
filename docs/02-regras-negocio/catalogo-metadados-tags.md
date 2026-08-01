# Catálogo, metadados e tags

Cadastro lógico, busca, filtros, visualização e classificação dos arquivos.

> Origem: documento mestre v0.12. As numerações originais foram mantidas para rastreabilidade.

## 24. Catálogo e metadados

O PostgreSQL manterá somente dados de controle e metadados, como:

- empresa;
- cliente;
- projeto;
- usuário responsável;
- máquina de origem;
- identificador interno;
- identificador do Drive;
- nome original;
- nome exibido;
- caminho ou pasta no Drive;
- extensão e tipo;
- tamanho;
- data da mídia;
- checksum;
- estado;
- progresso;
- link autorizado;
- datas de criação e atualização;
- estado de exclusão lógica.

### Campos funcionais editáveis

- nome;
- cliente;
- projeto;
- descrição;
- tags;
- data de gravação;
- observações;
- outros campos funcionais adicionados futuramente.

### Campos técnicos não editáveis manualmente

- IDs internos e do Drive;
- checksum;
- tamanho confirmado;
- estados técnicos;
- autoria e datas de auditoria;
- identificadores de máquina e sessão.

Descrições, observações e tags pertencerão somente ao catálogo. Não serão enviadas ao Drive.

### Cliente ou projeto alterado após upload

O sistema perguntará:

- alterar apenas o catálogo;
- alterar o catálogo e mover o arquivo no Drive;
- cancelar.

Pasta atual e destino serão mostrados. Nada será movido sem autorização.

---


## 25. Busca, filtros e visualização

A busca deverá incluir:

- nome;
- cliente;
- projeto;
- data;
- extensão;
- tipo;
- tamanho;
- tags;
- status;
- usuário responsável.

Não serão necessários filtros específicos por máquina de origem ou dispositivo nesta fase.

O frontend deverá mostrar, quando disponível:

- miniaturas de imagens;
- prévias de vídeos;
- player de áudio;
- estado de disponibilidade do arquivo.

Proprietários veem todo o catálogo da empresa. Administradores veem apenas arquivos de projetos autorizados.

---


## 26. Tags

- existirão tags genéricas fornecidas pelo sistema;
- Proprietários poderão criar tags personalizadas;
- tags serão armazenadas somente no catálogo;
- regras de edição e remoção das tags ainda podem ser detalhadas.

---


### Catálogo

- tags genéricas iniciais: `Bruto`, `Selecionado`, `Em edição`, `Em revisão`, `Aprovado`, `Final`, `Publicado` e `Arquivado`;
- Administradores poderão aplicar e remover tags em projetos autorizados;
- somente Proprietários poderão criar, renomear, arquivar ou excluir tags personalizadas;
- toda alteração de metadados manterá autor, data, valor anterior e valor novo;
- somente Proprietários poderão restaurar versões anteriores de metadados;
- além dos campos técnicos obtidos automaticamente, somente empresa, cliente e projeto serão obrigatórios;
- arquivo não localizado permanecerá no catálogo como `NAO_LOCALIZADO` e indisponível para download;
- Proprietários serão alertados e nenhuma exclusão ocorrerá automaticamente;
- se o arquivo reaparecer com a mesma identidade e integridade confirmada, será reconciliado automaticamente, com auditoria.


