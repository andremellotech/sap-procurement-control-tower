const assert=require('node:assert/strict');
const {scope,summarize}=require('../web/metrics.js');
const pr=(rc,centro,situacao)=>({rc,centro,grupo_compras:'G01',situacao});
const po=(pedido,centro,extra={})=>({pedido,centro,grupo_compras:'G01',status:'ABERTO',rc:'1',atrasado:1,saldo_milesimos:1000,valor_centavos:100,saldo_centavos:50,...extra});
const data={requisicoes:[pr('1','ENG','SEM_PEDIDO'),pr('1','ENG','PARCIAL'),pr('2','OPS','CONVERTIDA')],pedidos:[po('10','ENG'),po('10','ENG'),po('20','OPS',{rc:'',atrasado:0})]};
let k=summarize(scope(data,{centro:'ENG'}));
assert.equal(k.documentos_rc,1);assert.equal(k.itens_rc,2);assert.equal(k.documentos_pedido,1);assert.equal(k.saldo_centavos,100);assert.equal(k.rc_sem_pedido,1);
k=summarize(scope(data,{centro:'OPS'}));assert.equal(k.rc_convertida,1);assert.equal(k.itens_atrasados,0);assert.equal(k.pedidos_sem_rc,1);
k=summarize(scope(data,{grupo:'INEXISTENTE'}));assert.equal(k.itens_rc,0);assert.equal(k.saldo_centavos,0);
assert.equal(data.pedidos.length,3);
const fs=require('node:fs'),path=require('node:path');
const demoPath=path.join(__dirname,'../reports/demo/relatorio.json');
if(fs.existsSync(demoPath)){
 const demo=JSON.parse(fs.readFileSync(demoPath,'utf8'));
 assert.deepEqual(summarize(scope(demo)),demo.kpis);
 assert.equal(summarize(scope(demo,{centro:'ENG'})).saldo_centavos,764400);
}
console.log('Recortes de centro/grupo, contagem distinta e totais: OK');
