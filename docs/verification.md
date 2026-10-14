# Verificação da versão 1.0.0

Conferência local em 14/10/2026, Windows, Python 3.12.14 e Node.js do ambiente de trabalho.

## Regras e saídas

- `python -m unittest discover -s tests`: **16 testes aprovados** na rodada final do código funcional.
- `node --check web/app.js`, `node --check web/metrics.js` e `node tests/test_metrics.cjs`: aprovados. O teste JavaScript confronta os indicadores totais com os resultados efetivos das views SQL e o recorte ENG com 764.400 centavos.
- Cobertura: uma RC com vários pedidos, vários itens no mesmo documento, exclusão/conclusão, preço por 100, quantidade fracionária e arredondamento, vencimento hoje, recebido acima do pedido, referência desconhecida, unidade incompatível, duplicidade após normalização, pedido sem RC, backlog por liberação, nomes de colunas mapeados, formatos brasileiros, datas futuras e fórmulas XLSX.
- Exportação: banco/JSON/CSV com os mesmos totais, proteção de destino e entrada, escape HTML/CSV e preservação dos bytes de origem. Snapshot vazio mantém zeros e o esquema de colunas dos CSVs.
- O ciclo de testes reproduziu e corrigiu dois problemas: conexões SQLite abertas impediam a limpeza no Windows; exportações vazias perdiam as colunas esperadas. As regressões passaram após os ajustes.

O exemplo foi processado pelo código distribuído: 9 itens RC, 8 itens de pedido, 2 itens liberados sem pedido, 1 parcial, 5 itens com saldo e 3 atrasados. Os valores ativos/saldo/atraso são 70.444,00/12.044,00/8.919,00 BRL. O recorte ENG possui saldo 7.644,00 BRL e2 itens atrasados. Os cálculos SQL usam inteiros em centavos/milésimos.

## Navegador

Relatório aberto por HTTP local no navegador integrado. Foram conferidos:

- As cinco perspectivas, rastreabilidade RC 1000001001/item 00010 com dois pedidos e item00020 com pedido ativo e excluído.
- Ficha do pedido 4500002002 com saldo 7.500,00 BRL e referência RC  1000001001/item 00010; ligação ao roteiro ME23N com número/item conservados no quadro didático.
- Recorte ENG; recorte sem interseção OPS/G01 zerando indicadores e lista; busca inexistente exibindo estado vazio.
- Exportação real pelo navegador da busca 4500002003: CSV baixado com exatamente uma linha e saldo 14400 centavos.
- Layout desktop e larguras 390/320 px no guia, listas, ficha e identificação expandida. A página e a ficha não transbordaram; tabelas longas mantêm rolagem própria.
- Nenhum aviso/erro de console durante a navegação. Capturas reais da visão geral, rastreabilidade e guia em `docs/images/`.

## Alcance e limites

Revisão de código e verificação local realizadas nesta sessão. Revisão independente por agente não foi realizada devido ao limite de uso informado anteriormente na sessão. Não há declaração de homologação em um SAP real, recálculo nativo Power BI ou execução remota dos seis jobs de CI. As referências oficiais fundamentam o papel das transações; o contrato analítico e seus quadros didáticos não reproduzem um layout universal SAP.

O pacote é conferido por integridade ZIP, estrutura/links e reprodução de `build` e `demo` a partir de uma cópia extraída, com conferência dos totais e hashes de fontes. O Pages e os workflows precisam ser ativados/enviados e conferidos no GitHub após publicação manual.
