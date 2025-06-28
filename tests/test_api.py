import unittest, requests
import signal

class TestAPI(unittest.TestCase):

    target_URL = 'http://localhost:8000'

    def test_chegar_servidor(self):
        # Testar se a gente consegue chegar no servidor.
        requests.get(f'{self.target_URL}/')

    def test_criar_pesquisa(self):
        pass

    def test_ja_existe_pesquisa(self):
        pass


if __name__ == '__main__':
    unittest.main()
