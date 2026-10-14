import csv
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

try:
    from procurement.engine import analyze
    from procurement.io import load_input
except ImportError:
    analyze = load_input = None

ROOT = Path(__file__).resolve().parents[1]
DATE = '2026-09-30'

def pr(**changes):
    value = dict(rc='1000001001', item_rc='00010', data_rc='2026-09-01', data_liberacao='2026-09-02', solicitante='Pessoa fictícia', centro='ENG', grupo_compras='G01', material='MAT1', descricao='Material fictício', unidade='UN', quantidade_milesimos=100000, status='LIBERADA', arquivo='requisicoes.csv', linha=2)
    return {**value, **changes}

def po(**changes):
    value = dict(pedido='4500002001', item_pedido='00010', rc='1000001001', item_rc='00010', data_pedido='2026-09-05', fornecedor='Fornecedor Alfa', centro='ENG', grupo_compras='G01', material='MAT1', descricao='Material fictício', unidade='UN', quantidade_milesimos=60000, recebido_milesimos=10000, preco_centavos=25000, unidade_preco=1, data_prevista='2026-09-20', status='ABERTO', arquivo='pedidos.csv', linha=2)
    return {**value, **changes}

def data(requests=None, orders=None):
    return {'requisicoes': requests if requests is not None else [pr()], 'pedidos': orders if orders is not None else [po()], 'fontes': {}}

class EngineTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(analyze, 'O motor e o leitor ainda precisam ser implementados')

    def test_one_request_multiple_orders_without_multiplying_demand(self):
        result = analyze(data(orders=[po(), po(pedido='4500002002', quantidade_milesimos=40000, recebido_milesimos=40000, status='CONCLUIDO')]), DATE)
        self.assertEqual(len(result['requisicoes']), 1)
        self.assertEqual(result['requisicoes'][0]['quantidade_milesimos'], 100000)
        self.assertEqual(result['requisicoes'][0]['pedido_milesimos'], 100000)
        self.assertEqual(result['requisicoes'][0]['situacao'], 'CONVERTIDA')
        self.assertEqual(result['kpis']['valor_pedidos_centavos'], 2500000)
        self.assertEqual(result['kpis']['saldo_centavos'], 1250000)

    def test_multiple_items_in_one_order_count_as_one_document(self):
        result=analyze(data(orders=[po(),po(item_pedido='00020',quantidade_milesimos=40000)]),DATE)
        self.assertEqual(result['kpis']['documentos_pedido'],1)
        self.assertEqual(result['kpis']['itens_pedido'],2)
        self.assertEqual(result['requisicoes'][0]['pedido_milesimos'],100000)

    def test_header_alias_and_duplicate_after_identifier_normalization(self):
        import json
        with tempfile.TemporaryDirectory() as temp:
            target=Path(temp)
            for name in ('requisicoes.csv','pedidos.csv'):
                (target/name).write_bytes((ROOT/'sample-input'/name).read_bytes())
            mapping=json.loads((ROOT/'config/mapping.json').read_text(encoding='utf-8'))
            mapping['requisicoes']['colunas']['quantidade']='Quantidade solicitada'
            path=target/'requisicoes.csv'
            content=path.read_text(encoding='utf-8').replace(';quantidade;',';Quantidade solicitada;',1)
            path.write_text(content,encoding='utf-8')
            loaded=load_input(target,mapping,DATE)
            self.assertEqual(loaded['requisicoes'][0]['quantidade_milesimos'],100000)
            duplicate=content.splitlines()[1].replace(';10;',';00010;',1)
            path.write_text(content.rstrip()+'\n'+duplicate+'\n',encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'duplicado'):
                analyze(load_input(target,mapping,DATE),DATE)

    def test_canceled_po_reopens_request_and_closed_po_has_no_pending_delivery(self):
        result = analyze(data(orders=[po(status='EXCLUIDO'), po(pedido='4500002002', quantidade_milesimos=20000, recebido_milesimos=0, status='CONCLUIDO')]), DATE)
        self.assertEqual(result['requisicoes'][0]['saldo_rc_milesimos'], 80000)
        self.assertEqual(result['kpis']['itens_com_saldo'], 0)
        self.assertEqual(result['kpis']['saldo_centavos'], 0)
        self.assertEqual(len(result['pedidos']), 2)

    def test_price_per_100_fractional_quantity_and_half_up_cents(self):
        result = analyze(data(orders=[po(quantidade_milesimos=8000, recebido_milesimos=0, preco_centavos=180000, unidade_preco=100)]), DATE)
        self.assertEqual(result['pedidos'][0]['valor_centavos'], 14400)
        half = analyze(data(orders=[po(quantidade_milesimos=500, recebido_milesimos=0, preco_centavos=1)]), DATE)
        self.assertEqual(half['pedidos'][0]['valor_centavos'], 1)

    def test_due_today_is_not_late_and_overdelivery_is_visible(self):
        result = analyze(data(orders=[po(data_prevista=DATE)]), DATE)
        self.assertEqual(result['kpis']['itens_atrasados'], 0)
        result = analyze(data(orders=[po(recebido_milesimos=65000)]), DATE)
        self.assertEqual(result['kpis']['saldo_centavos'], 0)
        self.assertIn('RECEBIMENTO_SUPERIOR', [a['codigo'] for a in result['alertas']])

    def test_unknown_reference_unit_mismatch_and_duplicate_keys_rejected(self):
        for orders in ([po(rc='9999999999')], [po(unidade='KG')], [po(), po()]):
            with self.subTest(orders=orders):
                with self.assertRaises(ValueError):
                    analyze(data(orders=orders), DATE)

    def test_standalone_po_is_kept_separate_and_no_negative_backlog(self):
        result = analyze(data(orders=[po(rc='', item_rc=''), po(pedido='4500002002', quantidade_milesimos=110000)]), DATE)
        self.assertEqual(result['kpis']['pedidos_sem_rc'], 1)
        self.assertEqual(result['requisicoes'][0]['saldo_rc_milesimos'], 0)
        self.assertIn('PEDIDO_SUPERIOR_RC', [a['codigo'] for a in result['alertas']])

    def test_approval_waiting_and_excluded_requests_not_in_released_backlog(self):
        result = analyze(data(requests=[pr(status='AGUARDANDO', data_liberacao=''), pr(rc='1000001002', status='EXCLUIDA')], orders=[]), DATE)
        self.assertEqual(result['kpis']['rc_sem_pedido'], 0)
        self.assertEqual(result['kpis']['rc_aguardando'], 1)

    def test_known_demo_totals_and_read_snapshot(self):
        loaded = load_input(ROOT / 'sample-input', ROOT / 'config/mapping.json', DATE)
        result = analyze(loaded, DATE)
        self.assertEqual(result['kpis'], {'itens_rc': 9, 'documentos_rc': 8, 'itens_pedido': 8, 'documentos_pedido': 8, 'rc_sem_pedido': 2, 'rc_parcial': 1, 'rc_convertida': 3, 'rc_aguardando': 1, 'itens_com_saldo': 5, 'itens_atrasados': 3, 'valor_pedidos_centavos': 7044400, 'saldo_centavos': 1204400, 'saldo_atrasado_centavos': 891900, 'pedidos_sem_rc': 1})
        self.assertEqual(len(result['fontes']), 2)
        self.assertEqual(len(result['fontes']['pedidos.csv']['sha256']), 64)

    def test_csv_mapping_br_numbers_ids_and_duplicate_normalized_ids(self):
        import json
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp)
            mapping = json.loads((ROOT / 'config/mapping.json').read_text(encoding='utf-8'))
            for key in ('requisicoes', 'pedidos'):
                source = ROOT / 'sample-input' / (key + '.csv')
                (target / source.name).write_bytes(source.read_bytes())
            mapping['formato_data'] = 'br'
            mapping['decimal'] = ','
            mapping['milhar'] = '.'
            for key in ('requisicoes', 'pedidos'):
                path = target / (key + '.csv')
                with path.open(encoding='utf-8-sig', newline='') as stream:
                    reader = csv.DictReader(stream, delimiter=';')
                    fields, rows = reader.fieldnames, list(reader)
                for r in rows:
                    for f in ('data_rc', 'data_liberacao', 'data_pedido', 'data_prevista'):
                        if r.get(f):
                            y, m, d = r[f].split('-'); r[f] = f'{d}/{m}/{y}'
                    for f in ('quantidade', 'quantidade_recebida', 'preco_brl'):
                        if f in r:
                            r[f] = r[f].replace('.', ',')
                with path.open('w', encoding='utf-8', newline='') as stream:
                    writer = csv.DictWriter(stream, fields, delimiter=';'); writer.writeheader(); writer.writerows(rows)
            loaded = load_input(target, mapping, DATE)
            self.assertEqual(analyze(loaded, DATE)['kpis']['saldo_centavos'], 1204400)
            self.assertEqual(loaded['requisicoes'][0]['item_rc'], '00010')

    def test_input_rejects_future_creation_and_excel_formulas(self):
        import json
        import openpyxl
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp)
            for name in ('requisicoes.csv', 'pedidos.csv'):
                (target / name).write_bytes((ROOT / 'sample-input' / name).read_bytes())
            path = target / 'requisicoes.csv'
            path.write_text(path.read_text(encoding='utf-8').replace('2026-09-01', '2027-09-01', 1), encoding='utf-8')
            with self.assertRaises(ValueError):
                load_input(target, ROOT / 'config/mapping.json', DATE)
            mapping = json.loads((ROOT / 'config/mapping.json').read_text(encoding='utf-8'))
            mapping['requisicoes']['arquivo'] = 'requisicoes.xlsx'
            book = openpyxl.Workbook(); sheet = book.active; sheet.title = 'Dados'
            with (ROOT / 'sample-input/requisicoes.csv').open(encoding='utf-8-sig', newline='') as stream:
                for r in csv.reader(stream, delimiter=';'): sheet.append(r)
            book.save(target / 'requisicoes.xlsx')
            self.assertEqual(len(load_input(target, mapping, DATE)['requisicoes']), 9)
            sheet['I2'] = '=1+1'; book.save(target / 'requisicoes.xlsx')
            with self.assertRaisesRegex(ValueError, 'fórmula|Fórmula'):
                load_input(target, mapping, DATE)

if __name__ == '__main__': unittest.main()
