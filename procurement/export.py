"""Entrega autocontida, sem CDN nem comunicação com um ambiente SAP."""
import csv
from contextlib import closing
from datetime import datetime,timezone
import json
from pathlib import Path
import re
import sqlite3
from uuid import uuid4
from . import __version__
from .engine import analyze,ROOT
from .io import load_input

def safe_cell(value):
    if isinstance(value,str) and value.lstrip().startswith(('=','+','-','@')): return "'"+value
    return value

def write_csv(path,rows,headers):
    with path.open('w',encoding='utf-8-sig',newline='') as stream:
        writer=csv.DictWriter(stream,headers,delimiter=';')
        writer.writeheader()
        writer.writerows({k:safe_cell(v) for k,v in row.items()} for row in rows)

def render(result,path,prefix=''):
    template=(ROOT/'web/template.html').read_text(encoding='utf-8')
    context={'downloadPrefix':prefix,'guide':json.loads((ROOT/'config/gui-guide.json').read_text(encoding='utf-8'))}
    def encode(value): return json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False).replace('<','\\u003c')
    replacements={'__CSS__':(ROOT/'web/style.css').read_text(encoding='utf-8'),'__METRICS__':(ROOT/'web/metrics.js').read_text(encoding='utf-8'),'__JS__':(ROOT/'web/app.js').read_text(encoding='utf-8'),'__DATA__':encode(result),'__CONTEXT__':encode(context)}
    path.write_text(re.sub(r'__[A-Z_]+__',lambda m:replacements.get(m[0],m[0]),template),encoding='utf-8')

def build(input_dir,mapping,as_of,output,*,demonstrative=False,overwrite_demo=False):
    source,target=Path(input_dir).resolve(),Path(output).resolve()
    if source==target or source in target.parents: raise ValueError('A saída precisa ficar fora da entrada')
    if target.exists() and (not target.is_dir() or any(target.iterdir())) and not overwrite_demo:
        raise ValueError('Destino ocupado; escolha uma pasta vazia. Arquivos existentes preservados.')
    loaded=load_input(source,mapping,as_of)
    # Processar em memória primeiro evita criar saída para uma referência inválida.
    with closing(sqlite3.connect(':memory:')) as db:
        result=analyze(loaded,as_of,db)
        result['demonstrativo']=demonstrative
        result['execucao']={'id':str(uuid4()),'gerado_em_utc':datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z'),'versao':__version__}
        def check_safe(value):
            if type(value) is int and abs(value)>9007199254740991: raise ValueError('Volume excede a precisão inteira segura do relatório visual')
            if isinstance(value,dict):
                for v in value.values(): check_safe(v)
            elif isinstance(value,list):
                for v in value: check_safe(v)
        check_safe(result)
        target.mkdir(parents=True,exist_ok=True)
        # Somente os arquivos gerados conhecidos são substituídos por demo.
        if overwrite_demo and (target/'compras.sqlite').exists(): (target/'compras.sqlite').unlink()
        with closing(sqlite3.connect(target/'compras.sqlite')) as destination: db.backup(destination)
    for key in ('requisicoes','pedidos','fornecedores','alertas'): write_csv(target/(key+'.csv'),result[key],result['colunas'][key])
    (target/'relatorio.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    render(result,target/'index.html')
    return result
