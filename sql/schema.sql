-- Uma linha por documento + item. Dados monetários e quantidades são inteiros.
CREATE TABLE snapshot(data_corte TEXT NOT NULL);
CREATE TABLE requisicoes (
 rc TEXT, item_rc TEXT, data_rc TEXT, data_liberacao TEXT, solicitante TEXT,
 centro TEXT, grupo_compras TEXT, material TEXT, descricao TEXT, unidade TEXT,
 quantidade_milesimos INTEGER, status TEXT, arquivo TEXT, linha INTEGER,
 PRIMARY KEY(rc,item_rc)
);
CREATE TABLE pedidos (
 pedido TEXT, item_pedido TEXT, rc TEXT, item_rc TEXT, data_pedido TEXT,
 fornecedor TEXT, centro TEXT, grupo_compras TEXT, material TEXT, descricao TEXT,
 unidade TEXT, quantidade_milesimos INTEGER, recebido_milesimos INTEGER,
 preco_centavos INTEGER, unidade_preco INTEGER, data_prevista TEXT,
 status TEXT, arquivo TEXT, linha INTEGER, PRIMARY KEY(pedido,item_pedido)
);
CREATE INDEX pedido_origem_rc ON pedidos(rc,item_rc);
