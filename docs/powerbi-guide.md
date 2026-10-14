# Usar as saídas no Power BI

Esta versão entrega SQL, CSVs e relatório HTML; não inclui um PBIX homologado. Este roteiro é um ponto de partida para criar seu próprio modelo e confrontá-lo com os valores conhecidos.

1. Importe `reports/demo/requisicoes.csv` e `pedidos.csv` como UTF-8, separador ponto e vírgula.
2. No Power Query, force rc/item_rc/pedido/item_pedido como **Texto**, antes de conversões que removam zeros. Datas são ISO. Valores `_centavos` e quantidades `_milesimos` são **Número inteiro**.
3. Para começar, mantenha as duas tabelas de fatos em páginas separadas. Crie dimensões de Centro e Grupo com chaves únicas para filtrar ambas em direção única. Não una as bases linha a linha para somar a quantidade da RC, pois um item pode ter vários pedidos.
4. Se criar navegação cruzada por RC/item, modele uma dimensão de chave composta única que filtre as duas bases. Pedidos sem RC precisam de uma categoria própria, e itens sem pedido não podem desaparecer. Não acrescente simultaneamente uma relação direta entre as duas bases que gere caminhos ambíguos.
5. Recrie os indicadores e confronte o total com a saída SQL/JSON. A situação da RC já incorpora todos os seus pedidos no snapshot.

Medidas iniciais, usando nomes de tabelas `Requisicoes` e `Pedidos`:

```dax
Saldo a entregar BRL = DIVIDE(SUM(Pedidos[saldo_centavos]), 100)

Saldo atrasado BRL =
DIVIDE(
    CALCULATE(SUM(Pedidos[saldo_centavos]), Pedidos[atrasado] = 1),
    100
)

Itens RC sem pedido =
CALCULATE(COUNTROWS(Requisicoes), Requisicoes[situacao] = "SEM_PEDIDO")
```

Antes de publicar, confira a seleção por centro/grupo, a preservação dos zeros e os valores 12.044,00/8.919,00 BRL e 2 itens sem pedido no exemplo. Quantidades só devem ser somadas numa unidade compatível. Valide o novo modelo no Power BI; esses exemplos de medidas não representam um arquivo nativo testado.

Referência de modelagem: [esquema estrela e Power BI — Microsoft](https://learn.microsoft.com/en-us/power-bi/guidance/star-schema).
