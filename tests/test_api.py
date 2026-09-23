import unittest, tempfile, sys
from os import environ
from pathlib import Path

# O BD de testes é um arquivo temporário, e precisa ser definido antes de importar a API.
_diretorio_temporario = tempfile.TemporaryDirectory()
environ["DB_PATH"] = str(Path(_diretorio_temporario.name) / "pesquisas_teste.db")
environ["GASOLINA_API_KEY"] = "chave-de-teste"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from api.main import app

CHAVE = {"X-API-Key": "chave-de-teste"}

def posto_importacao(id_posto, distribuidora='DISTRIBUIDORA 1', **precos):
    return {'id': id_posto, 'nome': f'POSTO FAKE {id_posto}', 'distribuidora': distribuidora,
            'endereco': f'Rua dos Bobos, {id_posto}', 'bairro': 'Centro', **precos}

class TestAPI(unittest.TestCase):

    # Os testes compartilham o BD, então cada um usa datas e IDs próprios.

    nomes_distribuidoras = ['DISTRIBUIDORA 1', 'DISTRIBUIDORA 2', 'DISTRIBUIDORA 3', 'DISTRIBUIDORA 4']

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_estamos_em_dev(self):
        # Estamos no ambiente de desenvolvimento?
        request_data = self.client.get('/environment').json()
        self.assertEqual(request_data['msg'], "DEV")

    ### Autenticação das rotas de escrita
    def test_escrita_exige_chave(self):
        request_data = self.client.post('/pesquisa/nova', json={'data': '20000101'})
        self.assertEqual(request_data.status_code, 401)

        request_data = self.client.post('/pesquisa/nova', json={'data': '20000101'},
                                        headers={"X-API-Key": "errada"})
        self.assertEqual(request_data.status_code, 401)

    ### Testes para a criação de pesquisas
    def test_criar_pesquisa_sem_data(self):
        # Não especificamos a data, então precisa falhar
        request_data = self.client.post('/pesquisa/nova', headers=CHAVE)
        self.assertEqual(request_data.status_code, 422)

    def test_criar_pesquisa_data_invalida(self):
        # A data precisa ser AAAAMMDD
        request_data = self.client.post('/pesquisa/nova', json={'data': '2026055'}, headers=CHAVE)
        self.assertEqual(request_data.status_code, 422)

    def test_criar_pesquisa(self):
        request_data = self.client.post('/pesquisa/nova', json={'data': '20100101'}, headers=CHAVE)
        json_output = request_data.json()

        self.assertEqual(request_data.status_code, 200)
        self.assertEqual(json_output['data'], '20100101')

        # E a mesma data de novo tem que falhar
        request_data = self.client.post('/pesquisa/nova', json={'data': '20100101'}, headers=CHAVE)
        self.assertEqual(request_data.status_code, 422)

        datas = [pesquisa["data"] for pesquisa in self.client.get('/pesquisas').json()]
        self.assertIn('20100101', datas)

    ### Testes para a criação de distribuidoras e postos
    def test_criar_distribuidoras_e_postos(self):
        for nome_distribuidora in self.nomes_distribuidoras:
            self.client.post('/distribuidora/nova', json={'nome': nome_distribuidora}, headers=CHAVE)

        distribuidoras_lidas = [d['nome'] for d in self.client.get('/distribuidoras').json()]
        for nome_distribuidora in self.nomes_distribuidoras:
            self.assertIn(nome_distribuidora, distribuidoras_lidas)

        # A distribuidora repetida tem que falhar
        request_data = self.client.post('/distribuidora/nova', json={'nome': 'DISTRIBUIDORA 1'}, headers=CHAVE)
        self.assertEqual(request_data.status_code, 422)

        ## O ID do posto vem da tabela, então por consistência nós vamos fornecer ele.
        dados_posto = {'id': 501, 'nome': 'POSTO FAKE 501', 'distribuidora': 'DISTRIBUIDORA 1',
                       'endereco': 'Rua dos Bobos, 0', 'bairro': 'Centro'}
        request_data = self.client.post('/posto/novo', json=dados_posto, headers=CHAVE)
        self.assertEqual(request_data.status_code, 200)

        # O posto já existe
        request_data = self.client.post('/posto/novo', json=dados_posto, headers=CHAVE)
        self.assertEqual(request_data.status_code, 422)

        # O posto tem uma distribuidora inválida
        request_data = self.client.post('/posto/novo', headers=CHAVE,
                                        json={**dados_posto, 'id': 502, 'distribuidora': 'DISTRIBUIDORA 999'})
        self.assertEqual(request_data.status_code, 422)

        # Posto sem bairro é aceito
        request_data = self.client.post('/posto/novo', headers=CHAVE,
                                        json={**dados_posto, 'id': 503, 'bairro': None})
        self.assertEqual(request_data.status_code, 200)

    ### Importação atômica
    def test_importar_pesquisa(self):
        importacao = {'data': '20200101',
                      'postos': [posto_importacao(601, 'DISTRIBUIDORA NOVA', comum=6.29, gnv=4.99),
                                 posto_importacao(602, comum=6.49)]}
        request_data = self.client.post('/pesquisa/importar', json=importacao, headers=CHAVE)
        self.assertEqual(request_data.status_code, 200)
        resultado = request_data.json()
        self.assertEqual(resultado['precos'], 2)
        self.assertIn('DISTRIBUIDORA NOVA', resultado['distribuidoras_novas'])

        precos = {p['id']: p for p in self.client.get(f"/pesquisa/{resultado['id']}").json()}
        self.assertEqual(float(precos['601']['gasolina_comum']), 6.29)
        self.assertEqual(float(precos['601']['GNV']), 4.99)
        self.assertIsNone(precos['602']['etanol'])

    def test_importacao_com_erro_nao_grava_nada(self):
        self.client.post('/pesquisa/nova', json={'data': '20200202'}, headers=CHAVE)

        # A data já existe: a distribuidora e o posto novos não podem ficar no BD.
        importacao = {'data': '20200202',
                      'postos': [posto_importacao(701, 'DISTRIBUIDORA ROLLBACK', comum=6.0)]}
        request_data = self.client.post('/pesquisa/importar', json=importacao, headers=CHAVE)
        self.assertEqual(request_data.status_code, 422)

        distribuidoras = [d['nome'] for d in self.client.get('/distribuidoras').json()]
        self.assertNotIn('DISTRIBUIDORA ROLLBACK', distribuidoras)
        self.assertEqual(self.client.get('/posto/701').json(), [])

    def test_importacao_com_ids_repetidos(self):
        importacao = {'data': '20200303',
                      'postos': [posto_importacao(801), posto_importacao(801)]}
        request_data = self.client.post('/pesquisa/importar', json=importacao, headers=CHAVE)
        self.assertEqual(request_data.status_code, 422)

    def test_ultima_pesquisa_e_a_mais_recente(self):
        # Carregar uma pesquisa antiga depois de uma nova não muda a "última".
        self.client.post('/pesquisa/importar', headers=CHAVE,
                         json={'data': '20990101', 'postos': [posto_importacao(901, comum=7.0)]})
        self.client.post('/pesquisa/importar', headers=CHAVE,
                         json={'data': '19990101', 'postos': [posto_importacao(901, comum=1.0)]})
        self.assertEqual(self.client.get('/ultima_pesquisa').json()['data'], '20990101')

    ### Páginas
    def test_paginas(self):
        self.assertEqual(self.client.get('/').status_code, 200)
        self.assertEqual(self.client.get('/historico/abc').status_code, 404)
        self.assertEqual(self.client.get('/historico/999999').status_code, 404)

        self.client.post('/pesquisa/importar', headers=CHAVE,
                         json={'data': '20210101', 'postos': [posto_importacao(1001, comum=6.0)]})
        self.assertEqual(self.client.get('/historico/1001').status_code, 200)


if __name__ == '__main__':
    unittest.main()
