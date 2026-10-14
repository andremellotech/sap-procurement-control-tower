-- Agregar pedidos ANTES do join evita multiplicar a quantidade da requisição.
CREATE VIEW vw_requisicoes AS
WITH atendimento AS (
 SELECT rc,item_rc,SUM(quantidade_milesimos) AS pedido_milesimos,
 COUNT(*) AS itens_pedido_ativos,MIN(data_pedido) AS primeiro_pedido
 FROM pedidos WHERE status <> 'EXCLUIDO' AND rc <> '' GROUP BY rc,item_rc
), base AS (
 SELECT r.*,COALESCE(a.pedido_milesimos,0) AS pedido_milesimos,
 COALESCE(a.itens_pedido_ativos,0) AS itens_pedido_ativos,a.primeiro_pedido,
 MAX(0,r.quantidade_milesimos-COALESCE(a.pedido_milesimos,0)) AS saldo_rc_milesimos
 FROM requisicoes r LEFT JOIN atendimento a USING(rc,item_rc)
)
SELECT b.*,
 CASE WHEN status <> 'LIBERADA' THEN status
      WHEN pedido_milesimos=0 THEN 'SEM_PEDIDO'
      WHEN saldo_rc_milesimos>0 THEN 'PARCIAL' ELSE 'CONVERTIDA' END AS situacao,
 CASE WHEN status='LIBERADA' AND saldo_rc_milesimos>0
      THEN CAST(julianday(s.data_corte)-julianday(data_liberacao) AS INTEGER) ELSE 0 END AS dias_aberta,
 CASE WHEN primeiro_pedido IS NOT NULL
      THEN CAST(julianday(primeiro_pedido)-julianday(data_rc) AS INTEGER) END AS dias_rc_primeiro_pedido
FROM base b CROSS JOIN snapshot s;

CREATE VIEW vw_pedidos AS
WITH saldo AS (
 SELECT p.*,
 CASE WHEN status='ABERTO' THEN MAX(0,quantidade_milesimos-recebido_milesimos) ELSE 0 END AS saldo_milesimos,
 -- Divisão inteira e arredondamento half-up; unidade de preço pode ser 100.
 CASE WHEN status<>'EXCLUIDO' THEN
 (quantidade_milesimos*preco_centavos+(1000*unidade_preco)/2)/(1000*unidade_preco) ELSE 0 END AS valor_centavos
 FROM pedidos p
), valorizado AS (
 SELECT a.*,(saldo_milesimos*preco_centavos+(1000*unidade_preco)/2)/(1000*unidade_preco) AS saldo_centavos,
 CASE WHEN saldo_milesimos>0 AND data_prevista<s.data_corte THEN 1 ELSE 0 END AS atrasado,
 CASE WHEN saldo_milesimos>0 AND data_prevista<s.data_corte
 THEN CAST(julianday(s.data_corte)-julianday(data_prevista) AS INTEGER) ELSE 0 END AS dias_atraso
 FROM saldo a CROSS JOIN snapshot s
)
SELECT v.*,CASE WHEN status='EXCLUIDO' THEN 'EXCLUIDO' WHEN status='CONCLUIDO' THEN 'CONCLUIDO'
 WHEN saldo_milesimos=0 THEN 'RECEBIDO' WHEN atrasado=1 THEN 'ATRASADO' ELSE 'NO_PRAZO' END AS situacao
FROM valorizado v;

CREATE VIEW vw_fornecedores AS
SELECT fornecedor,COUNT(*) AS itens,COUNT(DISTINCT pedido) AS documentos,
 SUM(valor_centavos) AS valor_centavos,SUM(saldo_centavos) AS saldo_centavos,
 SUM(atrasado) AS itens_atrasados,SUM(CASE WHEN atrasado=1 THEN saldo_centavos ELSE 0 END) AS saldo_atrasado_centavos
FROM vw_pedidos WHERE status<>'EXCLUIDO' GROUP BY fornecedor;

CREATE VIEW vw_indicadores AS SELECT
 (SELECT COUNT(*) FROM requisicoes) AS itens_rc,
 (SELECT COUNT(DISTINCT rc) FROM requisicoes) AS documentos_rc,
 (SELECT COUNT(*) FROM pedidos) AS itens_pedido,
 (SELECT COUNT(DISTINCT pedido) FROM pedidos) AS documentos_pedido,
 (SELECT COUNT(*) FROM vw_requisicoes WHERE situacao='SEM_PEDIDO') AS rc_sem_pedido,
 (SELECT COUNT(*) FROM vw_requisicoes WHERE situacao='PARCIAL') AS rc_parcial,
 (SELECT COUNT(*) FROM vw_requisicoes WHERE situacao='CONVERTIDA') AS rc_convertida,
 (SELECT COUNT(*) FROM vw_requisicoes WHERE situacao='AGUARDANDO') AS rc_aguardando,
 (SELECT COUNT(*) FROM vw_pedidos WHERE saldo_milesimos>0) AS itens_com_saldo,
 (SELECT COALESCE(SUM(atrasado),0) FROM vw_pedidos) AS itens_atrasados,
 (SELECT COALESCE(SUM(valor_centavos),0) FROM vw_pedidos) AS valor_pedidos_centavos,
 (SELECT COALESCE(SUM(saldo_centavos),0) FROM vw_pedidos) AS saldo_centavos,
 (SELECT COALESCE(SUM(saldo_centavos),0) FROM vw_pedidos WHERE atrasado=1) AS saldo_atrasado_centavos,
 (SELECT COUNT(*) FROM pedidos WHERE rc='' AND status<>'EXCLUIDO') AS pedidos_sem_rc;
