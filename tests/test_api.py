import unittest, requests
from datetime import datetime

class TestAPI(unittest.TestCase):

    target_URL = 'http://localhost:8000'


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
        today = str(datetime.now().strftime("%Y%m%d"))
        request_data = requests.post(f'{self.target_URL}/pesquisa/nova', json = {'data': today})

        json_output = request_data.json()
        self.assertEqual(request_data.status_code, 200)
        self.assertEqual(json_output['id'], 1)
        self.assertEqual(json_output['data'], today)

    def test_ja_existe_pesquisa(self):

        # então testar especificar com uma data
        today = str(datetime.now().strftime("%Y%m%d"))
        request_data = requests.post(f'{self.target_URL}/pesquisa/nova', json = {'data': today})

        json_output = request_data.json()
        self.assertEqual(request_data.status_code, 422)


if __name__ == '__main__':
    unittest.main()
