# Publicar pelo GitHub web

Nome do repositório: **sap-procurement-control-tower**. Conta de referência: **andremellotech**. O pacote já contém README, licença MIT, testes, exemplos e workflow. Ele não contém dados de empresa nem integração ativa com SAP.

1. Baixe o ZIP completo e use Extrair tudo. Abra a pasta interna `sap-procurement-control-tower`.
2. Crie o repositório público com esse nome, sem inicializar README/licença adicionais. Se já existir, atualize nele mesmo.
3. Use **Add file → Upload files** e arraste o conteúdo interno, com pastas inteiras. Não envie o ZIP nem nivele arquivos de pastas diferentes na raiz.
4. Confira `procurement/engine.py`, `sql/views.sql`, `reports/demo/compras.sqlite` e `.github/workflows/validate.yml`. Se aparecer apenas `engine.py`, cancele o envio e arraste as pastas do Explorador.
5. Faça o commit na branch apropriada. Mensagem sugerida: `Publicar SAP Procurement Control Tower v1.0.0`. Se sua branch exigir revisão, use uma branch nova e pull request pelo site.

O pacote fica abaixo de 100 arquivos e 25 MiB por arquivo para envio web. [Documentação de upload do GitHub](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository).

## Ativar o relatório visual

Em **Settings → Pages**, escolha **Deploy from a branch**, **main** e **/(root)**; salve. Aguarde o deployment e confirme **Visit site**. O endereço esperado é `https://andremellotech.github.io/sap-procurement-control-tower/`. Configure Website em About com a URL confirmada. [Configurar a publicação do Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).

Como o HTML já está gerado e há `.nojekyll`, não é necessário montar um workflow adicional de publicação. `Validate procurement` é somente validação de código/dados. Se `.github` não for enviada, adicione pelo editor web o arquivo `.github/workflows/validate.yml` copiando o conteúdo do pacote. Não amplie permissões de escrita para rodar os testes.

Após publicar, confira as cinco perspectivas, os vínculos, uma ficha e seu guia, filtros e downloads. Veja os seis jobs de teste na aba Actions. A execução remota só pode ser afirmada depois que o GitHub mostrar o resultado.

Descrição sugerida:

```text
Requisições e pedidos de compra com referência SAP GUI: rastreabilidade por item, SQL reproduzível e relatório visual com dados fictícios.
```

Tópicos sugeridos: sap, sap-gui, procurement, sql, python, data-analytics, portfolio.

Se mudar conta/nome, atualize os links no README e `web/template.html`, depois execute `demo`. Use o Pages para compartilhar a experiência visual; a aba Code conserva os arquivos para quem deseja reutilizar o projeto. Nunca envie suas pastas locais de entrada/configuração/saída no upload manual: `.gitignore` não filtra o que você escolhe enviar pela web.
