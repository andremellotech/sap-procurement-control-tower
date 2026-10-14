# Como usar

## Explorar sem instalar

Extraia o projeto completo e abra `index.html` no navegador. CSS, scripts e dados estão incorporados; mantenha `reports/demo` ao lado para os downloads funcionarem. No GitHub, use o link do Pages para interagir: a aba Code mostra HTML como código.

1. Na **Visão geral**, observe o corte, os documentos/itens e os quatro indicadores. Clique em Sem pedido, Atendimento parcial ou Com pedido para ir à lista correspondente.
2. Em **Requisições**, pesquise número ou material e filtre situação. Clique no número para abrir a ficha. **Acompanhar pedidos** abre a rastreabilidade daquele item.
3. Em **Pedidos**, consulte saldo, previsão e fornecedor. A ficha mostra preço e unidade de preço, origem e RC relacionada. **Ver roteiro ME23N** abre o guia com número/item do documento.
4. Em **Rastreabilidade**, selecione uma RC/item. Quantidades solicitadas não são repetidas para cada pedido. Pedidos excluídos aparecem, mas não entram no atendimento.
5. Em **Guia SAP GUI**, selecione ME53N, ME5A, ME23N ou ME2N. Leia o roteiro, os campos necessários e a referência oficial. O quadro é didático, sem acesso ao seu SAP.

Os filtros superiores de centro/grupo recortam os indicadores e as listas. A busca/situação modifica somente a lista atual e seu CSV. A situação da RC considera todos os seus pedidos no snapshot; a rastreabilidade também exibe todos os vínculos da RC selecionada. Limpar filtros restaura os recortes e a seleção de busca/situação.

Expanda **Dados, critérios e identificação** para ver UUID, horário UTC, hashes de fontes e links de download. O JSON completo, CSVs e SQLite não acompanham o filtro da tela: são o snapshot integral. **Exportar seleção CSV**, nas listas, acompanha a seleção visível. CSV usa `;`, UTF-8 e colunas monetárias explicitamente em centavos e quantidades em milésimos.

## Executar com seus dados

1. Instale Python 3.11+ e abra o terminal na raiz do projeto extraído. Se usar ambiente virtual, substitua `python` por seu executável ativo.
2. Execute `python -m pip install -r requirements.txt`.
3. Copie `config/mapping.json` para `local-config/mapping.json`. Prepare duas exportações em `local-input`, mantendo os originais; adapte cabeçalhos/status conforme o [contrato](data-contract.md).
4. Informe uma data de corte coerente com o momento/posição das extrações. Não use o corte demonstrativo para tratar automaticamente um histórico diferente.
5. Execute:

```bash
python -m procurement build --input local-input --mapping local-config/mapping.json --as-of 2026-09-30 --output local-output/revisao-01
```

Abra o HTML na saída e confronte uma amostra na ME53N/ME23N. Conte documentos e itens separadamente, confira a unidade de preço e interprete os alertas. Use uma nova saída vazia para cada revisão. Erro de leitura ou vínculo interrompe a geração; erro posterior de exportação pode deixar pasta parcial. Corrija a mensagem e use outro destino. A existência de um arquivo não comprova sucesso.

O comando não busca no SAP nem altera fontes. `0` significa que gerou o relatório, não aprovação dos dados; `1` indica erro de processamento; erros de argumentos do terminal retornam `2` pelo argparse. Não compartilhe relatórios de dados particulares no repositório público.

## Recriar o exemplo

```bash
python -m procurement demo
```

O exemplo usa os CSVs fictícios versionados e o corte 2026-09-30. Se alterar o motor, SQL, mapeamento ou interface, rode os testes e `demo` antes de publicar as saídas atualizadas. `demo` não recria entradas que você tenha editado; conserve a amostra original para reproduzir os valores esperados.
