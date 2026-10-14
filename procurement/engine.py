"""Regras de referência e execução das consultas SQL distribuídas no repositório."""
from datetime import date
from pathlib import Path
import sqlite3

ROOT=Path(__file__).resolve().parents[1]

def analyze(data,as_of,connection=None):
    date.fromisoformat(as_of)
    requests,orders=data['requisicoes'],data['pedidos']
    keys={}
    for r in requests:
        key=(r['rc'],r['item_rc'])
        if key in keys: raise ValueError('RC/item duplicado: '+' / '.join(key))
        keys[key]=r
    seen=set()
    alerts=[]
    for p in orders:
        key=(p['pedido'],p['item_pedido'])
        if key in seen: raise ValueError('Pedido/item duplicado: '+' / '.join(key))
        seen.add(key)
        if bool(p['rc'])!=bool(p['item_rc']): raise ValueError('Referência RC/item incompleta')
        if p['rc']:
            ref=keys.get((p['rc'],p['item_rc']))
            if not ref: raise ValueError('Pedido com RC/item não encontrado: '+p['pedido'])
            for f in ('unidade','material','centro'):
                if p[f]!=ref[f]: raise ValueError('Referência incompatível em '+f+': '+p['pedido'])
            if p['data_pedido']<ref['data_rc']: raise ValueError('Pedido anterior à RC: '+p['pedido'])
            if p['status']!='EXCLUIDO' and ref['status']!='LIBERADA':
                alerts.append({'codigo':'STATUS_RC_REVISAR','documento':p['pedido'],'item':p['item_pedido'],'mensagem':'Pedido ativo ligado a RC não marcada LIBERADA; confira o histórico e o mapeamento.','transacao':'ME53N'})
        if p['recebido_milesimos']>p['quantidade_milesimos']:
            alerts.append({'codigo':'RECEBIMENTO_SUPERIOR','documento':p['pedido'],'item':p['item_pedido'],'mensagem':'Recebido acima do pedido. Confira tolerâncias, estornos e a extração.','transacao':'ME23N'})
    db=connection or sqlite3.connect(':memory:')
    db.row_factory=sqlite3.Row
    try:
        db.executescript((ROOT/'sql/schema.sql').read_text(encoding='utf-8'))
        db.execute('INSERT INTO snapshot VALUES (?)',(as_of,))
        for table,rows in [('requisicoes',requests),('pedidos',orders)]:
            columns=[r['name'] for r in db.execute('PRAGMA table_info('+table+')')]
            db.executemany('INSERT INTO '+table+' VALUES ('+','.join('?' for _ in columns)+')',[[r.get(c) for c in columns] for r in rows])
        db.executescript((ROOT/'sql/views.sql').read_text(encoding='utf-8'))
        result={'colunas':{}}
        for key,view in [('requisicoes','vw_requisicoes'),('pedidos','vw_pedidos'),('fornecedores','vw_fornecedores')]:
            cursor=db.execute('SELECT * FROM '+view)
            result['colunas'][key]=[column[0] for column in cursor.description]
            result[key]=[dict(r) for r in cursor]
        result['colunas']['alertas']=['codigo','documento','item','mensagem','transacao']
        for r in result['requisicoes']:
            if r['pedido_milesimos']>r['quantidade_milesimos']:
                alerts.append({'codigo':'PEDIDO_SUPERIOR_RC','documento':r['rc'],'item':r['item_rc'],'mensagem':'Quantidade em pedidos ativos acima da RC; confira alterações e os vínculos por item.','transacao':'ME53N'})
        result.update(schema_versao=1,data_corte=as_of,moeda='BRL',kpis=dict(db.execute('SELECT * FROM vw_indicadores').fetchone()),alertas=alerts,fontes=data.get('fontes',{}),mapeamento=data.get('mapeamento',{}))
        # Campos recebidos são guardados separadamente do formato normalizado.
        result['campos_origem']={table:[{k:r[k] for k in ('arquivo','linha','campos_origem') if k in r} for r in rows] for table,rows in [('requisicoes',requests),('pedidos',orders)]}
        db.commit()
        return result
    finally:
        if connection is None: db.close()
