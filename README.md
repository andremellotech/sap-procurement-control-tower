# SAP Procurement Control Tower

**Da requisição ao pedido: um relatório visual por documento e item, com SQL reproduzível e guia de conferência no SAP GUI.**

[Abrir demonstração](https://andremellotech.github.io/sap-procurement-control-tower/) · [Como usar](docs/user-guide.md) · [Guia SAP GUI](docs/sap-gui-guide.md) · [Adaptar as extrações](docs/data-contract.md) · [Publicar pela web](docs/publish-guide.md)

Projeto de portfólio de [André Mello](https://github.com/andremellotech). **Dados inteiramente fictícios**, materiais e fornecedores genéricos. Demonstração independente; não é um produto oficial SAP e não se conecta a um ambiente SAP. O link online fica disponível depois de ativar o GitHub Pages. Offline, extraia o projeto completo e abra `index.html`.

![Central de compras: visão geral](docs/images/overview.jpg)

## O que o projeto responde

- Quais itens de RC liberados continuam sem pedido ou com atendimento parcial?
- Quais itens de pedido têm saldo a entregar e previsão vencida?
- Como uma RC se distribui em vários pedidos, sem duplicar a quantidade solicitada?
- De qual arquivo/linha veio o registro e em qual transação SAP GUI conferir o documento?

Na ficha de um pedido, **Ver roteiro ME23N** leva ao guia correspondente e conserva número e item. Na rastreabilidade, todos os pedidos ligados ao item da RC aparecem, inclusive os excluídos. O guia usa quadros didáticos próprios, com links para documentação oficial SAP; não contém capturas corporativas.

## Cinco perspectivas integradas

| Perspectiva | Conteúdo |
|---|---|
| Visão geral | Itens sem pedido, saldo a entregar, atraso, fornecedores e prioridades |
| Requisições | Quantidade solicitada, quantidade em pedidos ativos, saldo e situação |
| Pedidos | Fornecedor, RC de origem, previsão, quantidades e saldo valorizado |
| Rastreabilidade | Vínculos de uma RC/item com seus pedidos/itens e origem |
| Guia SAP GUI | Roteiros ME53N, ME5A, ME23N e ME2N ligados às fichas |

Centro e grupo de compras definem o recorte dos indicadores. Busca e situação filtram a lista e seu CSV. O atendimento da RC e a rastreabilidade usam todos os vínculos do snapshot, mesmo quando um pedido pertence a outro grupo.

## Um exemplo conferível

Corte fictício: **30/09/2026**, moeda BRL.

| Indicador | Resultado |
|---|---:|
| RCs / itens de RC | 8 / 9 |
| Pedidos / itens de pedido | 8 / 8 |
| Itens de RC liberados sem pedido | 2 |
| Itens de RC com atendimento parcial | 1 |
| Itens de RC integralmente convertidos em pedido | 3 |
| Itens de pedido com saldo / atrasados | 5 / 3 |
| Valor dos pedidos ativos | R$ 70.444,00 |
| Saldo a entregar valorizado | R$ 12.044,00 |
| Saldo em atraso valorizado | R$ 8.919,00 |

O exemplo inclui atendimento por vários pedidos, pedido excluído, compra sem referência a RC, recebimento parcial e preço por 100 unidades. Um alerta expõe quantidade em pedidos ativos superior à quantidade da RC. Saldo valorizado é uma estimativa operacional pelo preço informado, sem tributos/frete; não é custo realizado ou compromisso contábil. Veja as [regras dos indicadores](docs/metrics.md).

## Reproduzir no computador

Python 3.11 ou posterior. Na raiz extraída:

```bash
python -m pip install -r requirements.txt
python -m procurement build --input sample-input --mapping config/mapping.json --as-of 2026-09-30 --output local-output/primeira-execucao
```

Abra `local-output/primeira-execucao/index.html`. O comando valida os arquivos e gera HTML autocontido, JSON, CSVs e banco SQLite com tabelas e consultas. Use uma saída vazia fora da entrada; arquivos recebidos não são modificados. Retorno **0** significa relatório gerado, mesmo com alertas de conferência; **1** indica erro. Isso não aprova o processo de compras.

Para recriar a demonstração pública fictícia: `python -m procurement demo`. Este comando atualiza somente os arquivos demonstrativos conhecidos em `reports/demo` e o `index.html` principal. Para seus dados, use `build` em pasta separada. Consulte o [passo a passo](docs/user-guide.md).

## Organização para reutilização

```text
procurement/       Leitura, validação, motor SQL e geração do relatório
sql/               Tabelas e views SQL comentadas, realmente executadas
sample-input/      Duas extrações fictícias CSV
config/            Mapeamento de colunas/formatos e guia SAP GUI
reports/demo/      Resultados já processados, CSVs, JSON e SQLite
web/               Interface sem CDN ou serviços externos
docs/              Guias de uso, indicadores, extração e publicação
tests/             Regras, leitura/exportação e recortes visuais
.github/workflows/ Validação configurada para Windows e Ubuntu
index.html         Demonstração pronta para abrir ou publicar no Pages
```

Aceita CSV UTF-8 e XLSX de valores, com mapeamento explícito. Os campos/estados do contrato são uma normalização do projeto: não representam um layout SAP universal. Preserve zeros nos documentos, a unidade de medida e a unidade de preço. O [contrato](docs/data-contract.md) explica como adaptar sua exportação. Há também um [roteiro para levar os dados ao Power BI](docs/powerbi-guide.md); nenhum `.pbix` nativo é incluído nesta versão.

## Verificar e contribuir

```bash
python -m unittest discover -s tests
node --check web/app.js
node --check web/metrics.js
node tests/test_metrics.cjs
```

Node.js é usado nos testes da interface; a rotina local executa em Python com SQLite. A matriz CI está configurada para Windows/Ubuntu e Python 3.11/3.12/3.13. Os resultados remotos dependem de enviar o workflow ao GitHub. Consulte o [registro de verificação](docs/verification.md) e [CONTRIBUTING](CONTRIBUTING.md).

## Limites e evolução

Esta versão cobre materiais com um centro, uma unidade e uma previsão por item, em BRL. Serviços, rateio múltiplo, remessas, moedas diferentes e histórico de recebimentos/faturas exigem extensão do modelo. A data de corte é declarada: sem histórico não se reconstrói a posição passada nem se calcula entrega no prazo. O quadro de referência não abre nem altera transações SAP.

Próximas extensões possíveis: histórico de eventos, remessas de entrega, recebimento/fatura, perfis de exportação adicionais e arquivo Power BI homologado. Elas não fazem parte da entrega atual.

Código e exemplos fictícios sob [licença MIT](LICENSE). [LinkedIn de André Mello](https://www.linkedin.com/in/aamello/).
