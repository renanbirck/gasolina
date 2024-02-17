import unittest, sys

sys.path.append('..')

import database, sqlite3
from os import remove
from os.path import isfile

class TestDatabase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """ Queremos trabalhar a partir de um banco de dados zerado, para não infleunciar os testes.
        """
        try:
            remove('pesquisas_test.db')
        except:
            pass
    @classmethod
    def tearDownClass(cls):
        try:
            remove('pesquisas_test.db')
        except:
            pass
        
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
        # Definir um estado 'zerado' para rodar o teste
        
        for distribuidora in ['ALFA', 'BETA', 'GAMA']:
            test_DB.cursor.execute("DELETE FROM Distribuidoras WHERE NomeDistribuidora=?;", (distribuidora, ))
            test_DB.cursor.execute("INSERT INTO Distribuidoras(NomeDistribuidora) VALUES(?);", (distribuidora,))
            test_DB.connection.commit()

        # tem que falhar, porque é repetida e isso viola a condição UNIQUE

        with self.assertRaises(sqlite3.IntegrityError) as context:
            test_DB.cursor.execute("INSERT INTO Distribuidoras(NomeDistribuidora) VALUES(?);", ("ALFA",))

    def test_quantidade_distribuidoras(self):
        test_DB = database.Database('pesquisas_test.db')
        test_DB.cursor.execute("SELECT COUNT(IdDistribuidora) from Distribuidoras;")
        output = test_DB.cursor.fetchone()
        self.assertEqual(output[0], 3)

    def test_adiciona_posto(self):
        test_DB = database.Database('pesquisas_test.db')
        test_DB.cursor.execute("INSERT INTO PostosGasolina(IdDistribuidora, NomePosto, EnderecoPosto, BairroPosto)\
                               VALUES ((SELECT IdDistribuidora FROM Distribuidoras WHERE NomeDistribuidora LIKE ?),\
                               ?, ?, ?)", ("ALFA", "Posto do Bozo", "Rua do Bozo, 0", "Centro"))
        test_DB.connection.commit()

    def test_adiciona_posto_repetido(self):
        test_DB = database.Database('pesquisas_test.db')
        with self.assertRaises(sqlite3.IntegrityError) as context:
            test_DB.cursor.execute("INSERT INTO PostosGasolina(IdDistribuidora, NomePosto, EnderecoPosto, BairroPosto)\
                                   VALUES ((SELECT IdDistribuidora FROM Distribuidoras WHERE NomeDistribuidora LIKE ?),\
                                   ?, ?, ?)", ("ALFA", "Posto do Bozo", "Rua do Bozo, 0", "Centro"))
            test_DB.connection.commit()


