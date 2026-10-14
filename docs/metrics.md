# Indicadores e consultas

O banco `compras.sqlite` contém as tabelas `requisicoes`, `pedidos` e `snapshot`, e as views reais distribuídas em `sql/views.sql`. Exemplo de consulta em um cliente SQLite:

```sql
SELECT * FROM vw_indicadores;
SELECT rc, item_rc, quantidade_milesimos, pedido_milesimos,
       saldo_rc_milesimos, situacao
FROM vw_requisicoes WHERE situacao IN ('SEM_PEDIDO','PARCIAL');
SELECT pedido, item_pedido, fornecedor, saldo_centavos, dias_atraso
FROM vw_pedidos WHERE atrasado = 1;
```

| Indicador | Regra |
|---|---|
| RC sem pedido | Item LIBERADA com quantidade em pedidos ativos igual a zero |
| RC parcial | Item LIBERADA com pedido ativo >0 e saldo de solicitação >0 |
| RC com pedido | Item LIBERADA com quantidade em pedidos ativos ≥ solicitada |
| Quantidade em pedidos | Soma por RC+item dos itens de pedido não EXCLUIDO, antes do join com a RC |
| Saldo da RC | Máximo entre zero e solicitado − quantidade em pedidos ativos |
| Dias abertos | Corte − liberação, somente para item LIBERADA sem atendimento completo |
| RC→primeiro pedido | Primeira criação de pedido ativo vinculado − criação da RC; não é tempo de aprovação |
| Saldo do pedido | Máximo entre zero e pedido − recebido, somente para ABERTO |
| Valor ativo | Quantidade × preço ÷ unidade de preço, exceto EXCLUIDO |
| Saldo valorizado | Saldo de quantidade × preço ÷ unidade de preço |
| Atrasado | Saldo positivo e data prevista anterior ao corte; vencendo hoje não é atraso |
| Pedido sem RC | Item não excluído, sem referência completa de origem |

Valores são arredondados half-up por item para centavos com divisão inteira. Quantidades estão em milésimos. O caso preço 1.800 BRL por 100 UN e quantidade 8 UN resulta em 144 BRL, não 14.400. Não somar quantidades de unidades/materiais diferentes como um indicador financeiro.

Compras ativas para uma RC podem exceder a demanda. O saldo da RC fica em zero e um alerta exige revisão; não há saldo negativo. Recebimento acima do pedido também é um alerta, pois tolerâncias podem existir. Nem todo alerta significa erro; nenhum é resolvido automaticamente.

O valor ativo preserva o valor do pedido concluído. O saldo do concluído é zero por definição operacional desta versão. Valores não incluem tributos, frete ou condições adicionais. Saldo a entregar não equivale a compromisso SAP, custo ou gasto realizado.

## Conferência do exemplo

9 itens de 8 RCs e 8 itens de 8 pedidos. Os itens de pedido excluídos não entram nos valores: total ativo 70.444,00 BRL; saldo 12.044,00 BRL; saldo atrasado 8.919,00 BRL.

Saldo de entrega em centavos por pedido: 4500002002=750000; 4500002003=14400; 4500002005=250000; 4500002006=127500; 4500002008=62500; demais zero. Só 2002, 2003 e 2006 estão atrasados no corte 2026-09-30.

RC 1000001001/item 00010 tem dois pedidos de 60 e 40 UN: solicitado 100, em pedidos 100 e saldo RC zero. RC 1000001001/item 00020 tem 8 UN em pedido ativo e 5 UN em pedido excluído: atendimento 8, saldo 12. RC 1000001006/item 00010 tem 45 UN compradas contra 40 solicitadas e gera alerta.

Filtros de centro/grupo selecionam cada base pelos seus próprios campos. O atendimento da RC já considera todos os pedidos vinculados no snapshot; o filtro não deve transformar um pedido conhecido em ausência. Na rastreabilidade, o recorte seleciona RCs e todos os pedidos dessas RCs são mostrados. Busca e situação recortam apenas a lista e seu CSV; downloads integrais continuam completos.
