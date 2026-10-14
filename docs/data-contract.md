# Contrato e adaptação de exportações

O contrato é **do projeto**, não um layout padronizado do SAP. Configure em `mapping.json` os nomes exatos dos cabeçalhos que você extraiu e faça a normalização dos status segundo as regras do seu ambiente. Nenhum código de liberação SAP é interpretado automaticamente.

## Arquivos e formatos

- Duas fontes: `requisicoes` e `pedidos`. Em cada seção configure `arquivo`, `aba` e `colunas` (campo interno → cabeçalho recebido).
- `arquivo` é um nome simples CSV/XLSX dentro de `--input`, sem subpastas. CSV: UTF-8 com BOM opcional, `separador` definido e cabeçalho na primeira linha. XLSX: aba definida, cabeçalho na primeira linha e valores tipados; fórmulas/erros de célula são rejeitados.
- `formato_data` é `iso` (AAAA-MM-DD) ou `br` (DD/MM/AAAA). Datas tipadas no Excel são aceitas.
- `decimal` é ponto ou vírgula e `milhar` é vazio, ponto ou vírgula, diferente do decimal. Agrupamento deve ser consistente; não há adivinhação de formato. Moeda e separadores não devem fazer parte do texto, por exemplo `R$ 10` é inválido.
- As colunas mapeadas são obrigatórias e distintas; cabeçalhos repetidos são rejeitados. Colunas extras são ignoradas e não são copiadas para o JSON.
- Uma linha por chave normalizada. Documentos numéricos de até 10 dígitos e itens de até 5 são preenchidos com zeros à esquerda. `10` e `00010` representam o mesmo item; duplicação após normalização é rejeitada.

O arquivo padrão usa cabeçalhos internos, CSV `;`, datas ISO e ponto decimal. Para XLSX, altere `arquivo` e `aba`; não basta trocar a extensão do arquivo. Para outros nomes, altere somente o valor correspondente em `colunas`, conservando todas as chaves internas.

## Requisições

| Campo | Conteúdo |
|---|---|
| rc, item_rc | Chave do item de requisição |
| data_rc | Criação, até a data de corte |
| data_liberacao | Data conferida; obrigatória em LIBERADA, entre criação e corte |
| solicitante | Identificação adequada ao caso; fictícia no exemplo |
| centro, grupo_compras | Identificadores usados no recorte |
| material, descricao, unidade | Identificação e unidade, com conteúdo obrigatório |
| quantidade | Quantidade solicitada positiva, até três casas |
| status | LIBERADA, AGUARDANDO, EXCLUIDA ou REJEITADA |

Não derive `data_liberacao` da criação nem de um status sozinho. Se a exportação não disponibilizar essa informação, obtenha uma fonte autorizada ou adapte o indicador/contrato conscientemente antes de aplicar o projeto.

## Pedidos

| Campo | Conteúdo |
|---|---|
| pedido, item_pedido | Chave única do item de pedido |
| rc, item_rc | Referência completa ou ambos vazios para compra sem RC |
| data_pedido | Criação até o corte e não anterior à RC vinculada |
| fornecedor | Chave/nome consistente na extração; não mesclar fornecedores homônimos |
| centro, grupo_compras | Identificadores organizacionais |
| material, descricao, unidade | Material/unidade/centro iguais aos da RC vinculada |
| quantidade | Quantidade positiva do pedido |
| quantidade_recebida | Recebido líquido não negativo; pode superar o pedido, com alerta para conferir tolerâncias/estornos |
| preco_brl | Preço não negativo com até duas casas, na moeda BRL |
| unidade_preco | Quantidade de unidades à qual o preço se refere: inteiro positivo, por exemplo 100 |
| data_prevista | Uma previsão por item, não anterior à criação do pedido |
| status | ABERTO, CONCLUIDO ou EXCLUIDO, normalizados pela regra confirmada no ambiente |

CONCLUIDO zera o saldo operacional mesmo que não tenha recebido toda a quantidade; o usuário precisa confirmar o significado dessa normalização. EXCLUIDO não entra no atendimento da RC nem nos valores ativos, mas conserva o vínculo. Em snapshots sem RC/item conhecidos, o projeto não infere uma correspondência por descrição ou material.

Quantidades aceitas até 1.000.000 e preço até 10.000.000BRL por unidade de preço; unidade de preço até 1.000.000. Esses limites mantêm produtos intermediários inteiros dentro da precisão definida. Quantidades e preços negativos exigem modelar devoluções/estornos antes de adaptar este contrato.

## Granularidade e controles

Várias linhas nativas por remessa ou rateio não podem ser importadas como vários itens iguais nem removidas arbitrariamente. Esta versão requer consolidar uma posição por item segundo uma regra validada, preservando o detalhe original para conferência. Materiais com unidades distintas exigem uma conversão explícita fora deste modelo. Um centro único por item é premissa da versão.

Antes da execução, confira quantidades de itens/documentos, totais na mesma moeda e uma amostra de referência RC→pedido no SAP. Datas, situação e recebido precisam representar o mesmo snapshot. O programa não comprova que o recebido pertence a um corte histórico sem eventos.

## Saídas

JSON e SQLite guardam valores monetários em inteiros `_centavos` e quantidades em `_milesimos`. CSV conserva os mesmos nomes/unidades; a tela formata BRL e a unidade do item. `arquivo` e `linha` preservam a origem; em CSV é a linha física inicial do registro, inclusive quando há texto multilinha. `fontes` guarda SHA-256 dos mesmos bytes lidos em memória. `campos_origem` conserva os campos mapeados antes da normalização.

Texto com início interpretável como fórmula recebe apóstrofo nos CSVs de saída, mantendo seu conteúdo no JSON. HTML escapa o texto exibido e incorpora os dados sem buscar serviços externos. O UUID identifica a saída; hash e UUID não são prova de autenticidade. Todos os dados enviados ao relatório ficam dentro do HTML; compartilhe somente o que estiver autorizado.
