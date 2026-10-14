import csv
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]

class ExportTests(unittest.TestCase):
    def test_empty_snapshot_preserves_csv_schema_and_zero_metrics(self):
        with tempfile.TemporaryDirectory() as temp:
            source=Path(temp)/'input';source.mkdir()
            for name in ('requisicoes.csv','pedidos.csv'):
                header=(ROOT/'sample-input'/name).read_text(encoding='utf-8').splitlines()[0]
                (source/name).write_text(header+'\n',encoding='utf-8')
            target=Path(temp)/'out'
            run=self.run_build(target,source)
            self.assertEqual(run.returncode,0,run.stderr)
            result=json.loads((target/'relatorio.json').read_text(encoding='utf-8'))
            self.assertEqual(result['kpis']['saldo_centavos'],0)
            with (target/'pedidos.csv').open(encoding='utf-8-sig',newline='') as stream:
                self.assertIn('saldo_centavos',csv.DictReader(stream,delimiter=';').fieldnames)
            with (target/'requisicoes.csv').open(encoding='utf-8-sig',newline='') as stream:
                self.assertIn('rc',csv.DictReader(stream,delimiter=';').fieldnames)

    def run_build(self, output, input_dir=None):
        return subprocess.run([sys.executable,'-B','-m','procurement','build','--input',str(input_dir or ROOT/'sample-input'),'--mapping',str(ROOT/'config/mapping.json'),'--as-of','2026-09-30','--output',str(output)],cwd=ROOT,capture_output=True,text=True)

    def test_cli_outputs_consistent_database_json_and_offline_report(self):
        with tempfile.TemporaryDirectory() as temp:
            target=Path(temp)/'saida'
            run=self.run_build(target)
            self.assertEqual(run.returncode,0,run.stderr)
            result=json.loads((target/'relatorio.json').read_text(encoding='utf-8'))
            self.assertEqual(result['kpis']['saldo_centavos'],1204400)
            with closing(sqlite3.connect(target/'compras.sqlite')) as db:
                self.assertEqual(db.execute('SELECT saldo_centavos FROM vw_indicadores').fetchone()[0],1204400)
            page=(target/'index.html').read_text(encoding='utf-8')
            self.assertIn(result['execucao']['id'],page)
            self.assertIn('Guia SAP',page)
            self.assertNotIn('<script src=',page)
            with (target/'pedidos.csv').open(encoding='utf-8-sig',newline='') as stream:
                self.assertEqual(sum(int(r['saldo_centavos']) for r in csv.DictReader(stream,delimiter=';')),1204400)

    def test_occupied_and_inside_input_outputs_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            target=Path(temp)
            (target/'sentinela.txt').write_text('preservar',encoding='utf-8')
            self.assertEqual(self.run_build(target).returncode,1)
            self.assertEqual((target/'sentinela.txt').read_text(encoding='utf-8'),'preservar')
            self.assertEqual(self.run_build(ROOT/'sample-input/nao-criar').returncode,1)
            self.assertFalse((ROOT/'sample-input/nao-criar').exists())

    def test_html_and_csv_escape_input_and_keep_source_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            source=Path(temp)/'in';source.mkdir()
            for name in ('requisicoes.csv','pedidos.csv'):
                (source/name).write_bytes((ROOT/'sample-input'/name).read_bytes())
            path=source/'pedidos.csv'
            content=path.read_text(encoding='utf-8').replace('Fornecedor Alfa','=1+1').replace('Conjunto de fixação','<img src=x onerror=alert(1)>')
            path.write_text(content,encoding='utf-8')
            before=path.read_bytes()
            target=Path(temp)/'out'
            run=self.run_build(target,source)
            self.assertEqual(run.returncode,0,run.stderr)
            self.assertEqual(path.read_bytes(),before)
            self.assertNotIn('<img src=x',(target/'index.html').read_text(encoding='utf-8'))
            with (target/'pedidos.csv').open(encoding='utf-8-sig',newline='') as stream:
                self.assertIn("'=1+1",[r['fornecedor'] for r in csv.DictReader(stream,delimiter=';')])

if __name__=='__main__': unittest.main()
