import unittest, sys

sys.path.append('..')

import database, sqlite3
from os import remove
from os.path import isfile

class TestDatabase(unittest.TestCase):


    def test_can_create_DB(self):
        """ Verificar se o DB pode ser criado, começando a partir de um DB virgem. """

        remove('pesquisas_test.db')

        test_DB = database.Database('pesquisas_test.db')
        self.assertEqual(isfile('pesquisas_test.db'), True)

    def test_do_tables_exist(self):
        """ Verificar se o DB foi corretamente inicializado, isto é, 
        se ele está persistindo (o D do ACID) a partir do teste anterior. """

        test_DB = database.Database('pesquisas_test.db')
        for table_name in ['Distribuidoras', 'PostosGasolina', 'Pesquisas', 'Precos']:
            # sqlite_master é onde estão os dados das tabelas.
            # Veja: https://stackoverflow.com/questions/1601151/
            result = test_DB.cursor.execute(f"SELECT name FROM sqlite_master WHERE name='{table_name}'").fetchone()
            self.assertIsNotNone(result)

    def test_adiciona_distribuidoras(self):
        test_DB = database.Database('pesquisas_test.db')

        for distribuidora in ['ALFA', 'BETA', 'GAMA']:
            test_DB.cursor.execute("INSERT INTO Distribuidoras(IdDistribuidora, NomeDistribuidora) VALUES(NULL,?);", (distribuidora,))

        # tem que falhar, porque é repetida

        with self.assertRaises(sqlite3.IntegrityError) as context:
            test_DB.cursor.execute("INSERT INTO Distribuidoras(IdDistribuidora, NomeDistribuidora) VALUES(NULL,?);", ("ALFA",))

    def test_adiciona_postos(self):
        pass


