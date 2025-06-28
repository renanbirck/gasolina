import unittest, requests
from datetime import datetime

class TestAPI(unittest.TestCase):

    target_URL = 'http://localhost:8000'
    today = str(datetime.now().strftime("%Y%m%d"))
    nomes_distribuidoras = ['DISTRIBUIDORA 1', 'DISTRIBUIDORA 2', 'DISTRIBUIDORA 3', 'DISTRIBUIDORA 4']

    def test_estamos_em_dev(self):
        # Estamos no ambiente de desenvolvimento?
        request_data = requests.get(f'{self.target_URL}/environment').json()
        self.assertEqual(request_data['msg'], "DEV")

    ### Testes para a criação de pesquisas
    def test_criar_pesquisa_sem_data(self):
        # Não especificamos a data, então precisa falhar
        request_data = requests.post(f'{self.target_URL}/pesquisa/nova')
        self.assertEqual(request_data.status_code, 422)

    def test_criar_pesquisa(self):
        # então testar especificar com uma data

        request_data = requests.post(f'{self.target_URL}/pesquisa/nova', json = {'data': self.today})
        json_output = request_data.json()

        self.assertEqual(request_data.status_code, 200)
        self.assertEqual(json_output['id'], 1)
        self.assertEqual(json_output['data'], self.today)

    def test_ja_existe_pesquisa(self):
        # então testar especificar com uma data

        request_data = requests.post(f'{self.target_URL}/pesquisa/nova', json = {'data': self.today})
        json_output = request_data.json()
        self.assertEqual(request_data.status_code, 422)

    def test_pegar_pesquisa(self):
        request_data = requests.get(f'{self.target_URL}/pesquisas').json()
        self.assertEqual(request_data[0]["id"], 1)
        self.assertEqual(request_data[0]["data"], self.today)

    ### Testes para a criação de distribuidoras

    def test_criar_distribuidoras(self):
        for nome_distribuidora in self.nomes_distribuidoras:
            # Cadastrar as distribuidoras ...
            request_data = requests.post(f'{self.target_URL}/distribuidora/nova',
                                         json = {'nome': nome_distribuidora})
            self.assertEqual(request_data.status_code, 200)
        # E testar se deu certo.

        request_data = requests.get(f'{self.target_URL}/distribuidoras').json()
        distribuidoras_lidas = [distribuidora['nome'] for distribuidora in request_data]
        for nome_distribuidora in distribuidoras_lidas:
            self.assertIn(nome_distribuidora, self.nomes_distribuidoras)





if __name__ == '__main__':
    unittest.main()
