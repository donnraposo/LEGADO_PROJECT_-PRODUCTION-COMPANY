# Visão e objetivos

Finalidade, visão, princípios, escala e glossário do produto.

> Origem: documento mestre v0.12. As numerações originais foram mantidas para rastreabilidade.

## 1. Finalidade deste documento

Este é o documento único de referência do projeto da produtora audiovisual. Ele deve permitir que uma pessoa ou outra IA compreenda:

- o objetivo do sistema;
- as regras já aprovadas;
- as decisões arquiteturais preliminares;
- o que ainda está pendente;
- o estado atual do trabalho;
- como continuar o projeto sem reinterpretar decisões anteriores.

As antigas fases de visão, análise técnica, arquitetura, estrutura, modelo de dados, roadmap, testes e decisões arquiteturais serão mantidas como seções deste mesmo arquivo, e não como vários documentos separados.

### Marcadores de estado

- **APROVADO:** decidido pelo usuário.
- **EM DISCUSSÃO:** assunto iniciado, mas ainda não encerrado.
- **PENDENTE:** ainda precisa ser discutido ou aprovado.
- **PLANEJADO:** aceito, mas ainda não iniciado.
- **EM IMPLEMENTAÇÃO:** desenvolvimento autorizado e em andamento.
- **CONCLUÍDO:** implementado e validado.
- **BLOQUEADO:** depende de decisão ou condição externa.

---


## 4. Visão do produto

### Objetivo

Construir uma plataforma para produtoras audiovisuais que:

1. acesse HDs externos, pen drives e outros dispositivos físicos;
2. organize arquivos por cliente, projeto e data de criação registrada pela câmera;
3. apresente uma prévia obrigatória antes de mover qualquer arquivo;
4. abra um frontend online após a organização;
5. permita selecionar e enviar arquivos ao Google Drive;
6. suporte arquivos audiovisuais de vários terabytes;
7. mantenha no PostgreSQL apenas catálogo, metadados, estados e auditoria;
8. permita consulta, edição, renomeação, download, arquivamento e envio à lixeira;
9. use n8n para orquestração sem transportar normalmente os grandes binários;
10. funcione com várias empresas, usuários e máquinas.

### Princípio de preservação

O sistema nunca poderá apagar definitivamente arquivos existentes na estação física. Ele poderá movê-los dentro do dispositivo durante a organização, após prévia e confirmação, mas não poderá eliminá-los.

### Escala esperada

- todos os formatos de arquivo devem ser aceitos para transporte e catálogo;
- cada trabalho pode conter alguns terabytes;
- o sistema será usado em várias máquinas;
- o frontend será online e acessível de qualquer local autorizado;
- Windows é a prioridade inicial; macOS é desejável se for viável.

---


## 5. Glossário

- **Agente local:** aplicação executada na máquina do usuário, com acesso autorizado aos dispositivos físicos.
- **Frontend:** interface online usada para operar e acompanhar o sistema.
- **Backend:** serviço central de autenticação, autorização, regras, estados e catálogo.
- **n8n:** orquestrador de integrações, eventos e sincronizações.
- **Drive:** Google Drive usado como armazenamento definitivo dos arquivos enviados.
- **Catálogo:** conjunto de metadados mantidos no PostgreSQL.
- **Dispositivo físico:** HD externo, pen drive ou mídia conectada à estação.
- **Organização:** movimentação local de arquivos para a estrutura Cliente/Projeto/Ano/Mês/Dia.
- **Lote:** conjunto de arquivos selecionados para organização, upload ou download.
- **Proprietário:** papel com controle máximo sobre uma empresa.
- **Administrador:** papel operacional com acesso limitado aos projetos atribuídos.

---


