# Reutilizar e contribuir

Leia o [contrato](docs/data-contract.md) e os [indicadores](docs/metrics.md) antes de adaptar dados ou regras. Mantenha sua cópia em um fork e trabalhe com entradas locais separadas dos exemplos públicos. Dados reais não devem acompanhar uma issue ou uma pull request.

Para corrigir uma regra, inclua um teste fictício com resultado conhecido. Preserve chaves documento+item, granularidade, unidade de preço, centavos e origem. Não substitua quantidades de uma RC por uma soma de joins que multiplique itens. Adapte serviços/remessas/rateios como um novo contrato explícito, não como colunas ignoradas silenciosamente.

Execute os comandos de teste do README. Mudanças visuais também exigem conferir filtros, fichas, navegação ao guia e telas pequenas. Depois de alterar código/SQL/interface, gere novamente a demonstração com `python -m procurement demo` e confronte os valores de referência.

Ao relatar um erro, informe versão, sistema/Python, comando, retorno e uma entrada mínima fictícia. Descreva o esperado e o obtido. O projeto não possui suporte oficial SAP nem pressupõe acesso ao seu ambiente.
