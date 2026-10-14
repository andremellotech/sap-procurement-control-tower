# Do SAP GUI ao relatório visual

A referência escolhida é **SAP GUI**. A SAP documenta ME51N/ME52N/ME53N para criar/alterar/exibir RC e ME21N/ME22N/ME23N para criar/alterar/exibir pedido. [Transações em tela única — SAP Help](https://help.sap.com/docs/SAP_ERP/967e1c2a6a8c4183b7e07d28e7574445/787db65334e6b54ce10000000a174cb4.html).

Para as listas, ME5A é a listagem de requisições e ME2N lista documentos por número. [Relatórios de compras — SAP Help](https://help.sap.com/docs/PRODUCT_ID/349992fb60854a62a264d716ad5c8f54/a1e5e052427c9d36e10000000a44538d.html).

Essas referências fundamentam as funções das transações. Os campos e estados do projeto são uma proposta de normalização analítica; não são uma afirmação de que todas as colunas existam em qualquer layout SAP. Consulte o responsável pelo ambiente para disponibilização, autorizações e semântica.

| No relatório | Onde conferir | O que investigar |
|---|---|---|
| RC sem pedido ou parcialmente atendida | ME53N; lista ME5A | Item, unidade, quantidade, liberação e acompanhamento disponíveis |
| Pedido com entrega pendente | ME23N; lista ME2N | Quantidade, previsão, recebido líquido, exclusão e conclusão |
| Diferença de valor | ME23N | Preço e unidade de preço, além de condições que este modelo não inclui |
| Um item de RC com vários pedidos | ME53N / ME23N | Referência explícita RC+item e quantidade de cada pedido |

## Preparar a extração

1. Defina a data de corte e o escopo organizacional que as duas bases representam.
2. Execute as listas com critérios e layouts que cubram todos os itens necessários. Um extrato só de pendentes não serve para reconstruir conversão de todas as RCs.
3. Exponha as chaves documento+item e as referências RC+item; mantenha códigos como texto ou normalize-os com o contrato documentado.
4. Obtenha datas e indicadores necessários de fontes autorizadas. Não invente data de liberação nem quantidade líquida recebida para completar o arquivo.
5. Exporte pelos recursos disponíveis na sua instalação e conserve o original. Registre critérios, layout, momento e responsável pela extração em sua documentação local.
6. Mapeie campos e status no formato do projeto, valide unidades, quantidades, número de itens e valores de uma amostra e processe a cópia local.
7. Use as fichas do relatório para voltar à conferência por transação e documento.

No painel, **Guia SAP GUI** detalha ME53N, ME5A, ME23N e ME2N. Clicar em Ver roteiro na ficha transporta o número/item para o quadro didático. O quadro não reproduz uma tela corporativa nem executa comandos. Criação/alteração ficam apenas identificadas como contexto do processo.

Recebimento/fatura e histórico de eventos são extensões futuras. O recebido da versão 1 é uma posição líquida informada, não movimentos que possam ser auditados por data. Serviços, rateios e remessas precisam de granularidade adicional antes de usar seus extratos aqui.
