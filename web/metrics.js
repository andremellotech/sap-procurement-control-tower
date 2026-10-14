/* Agregação do recorte visual: regras de atendimento e saldos vêm do SQL. */
var ProcurementMetrics=(()=>{
  function scope(data,filters={}){
    const match=r=>(!filters.centro||r.centro===filters.centro)&&(!filters.grupo||r.grupo_compras===filters.grupo);
    return {requisicoes:data.requisicoes.filter(match),pedidos:data.pedidos.filter(match)};
  }
  function summarize(data){
    const r=data.requisicoes,p=data.pedidos;
    const sum=(rows,f)=>rows.reduce((s,v)=>s+v[f],0),count=s=>r.filter(v=>v.situacao===s).length;
    return {itens_rc:r.length,documentos_rc:new Set(r.map(v=>v.rc)).size,itens_pedido:p.length,documentos_pedido:new Set(p.map(v=>v.pedido)).size,rc_sem_pedido:count('SEM_PEDIDO'),rc_parcial:count('PARCIAL'),rc_convertida:count('CONVERTIDA'),rc_aguardando:count('AGUARDANDO'),itens_com_saldo:p.filter(v=>v.saldo_milesimos>0).length,itens_atrasados:sum(p,'atrasado'),valor_pedidos_centavos:sum(p,'valor_centavos'),saldo_centavos:sum(p,'saldo_centavos'),saldo_atrasado_centavos:sum(p.filter(v=>v.atrasado),'saldo_centavos'),pedidos_sem_rc:p.filter(v=>!v.rc&&v.status!=='EXCLUIDO').length};
  }
  return {scope,summarize};
})();
if(typeof module!=='undefined')module.exports=ProcurementMetrics;
