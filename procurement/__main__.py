import argparse
from pathlib import Path
import sys
from .engine import ROOT
from .export import build,render

def main(argv=None):
    parser=argparse.ArgumentParser(description='RCs e pedidos de compra: análise local com referência SAP GUI')
    sub=parser.add_subparsers(dest='command',required=True)
    run=sub.add_parser('build',help='Validar extrações e gerar relatório local')
    run.add_argument('--input',required=True)
    run.add_argument('--mapping',default=str(ROOT/'config/mapping.json'))
    run.add_argument('--as-of',required=True,help='Data de corte AAAA-MM-DD coerente com o snapshot')
    run.add_argument('--output',required=True)
    sub.add_parser('demo',help='Recriar somente as saídas dos exemplos fictícios incluídos')
    args=parser.parse_args(argv)
    try:
        if args.command=='demo':
            result=build(ROOT/'sample-input',ROOT/'config/mapping.json','2026-09-30',ROOT/'reports/demo',demonstrative=True,overwrite_demo=True)
            render(result,ROOT/'index.html',prefix='reports/demo/')
            print('Demonstração atualizada em index.html; dados fictícios de 2026-09-30.')
        else:
            result=build(args.input,args.mapping,args.as_of,args.output)
            print(f"Relatório gerado em {Path(args.output)/'index.html'} | {len(result['alertas'])} alerta(s) | Execução {result['execucao']['id']}")
        return 0
    except Exception as exc:
        print('Erro: '+str(exc),file=sys.stderr);return 1

if __name__=='__main__': raise SystemExit(main())
