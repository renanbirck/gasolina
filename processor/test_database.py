import unittest, sys

sys.path.append('..')

import database
from os import remove
from os.path import isfile

class TestDatabase(unittest.TestCase):


    def test_can_create_DB(self):
        """ Verificar se o DB pode ser criado. """

        test_DB = database.Database()

        try:
            remove('pesquisas_test.db')
        except:
            pass

        test_DB.initialize_DB('pesquisas_test.db')
        self.assertEqual(isfile('pesquisas_test.db'), True)

    def test_adiciona_distribuidoras(self):
        pass

    def test_adiciona_postos(self):
        pass


