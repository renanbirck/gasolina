import unittest, sys
sys.path.append('..')

import parser_core

class TestParser(unittest.TestCase):

    target = 'references/Novembro-2023.pdf'

    def test_can_get_survey_info(self):
        parser = parser_core.PDFParser(self.target)
       
        # Testar se a gente está na pesquisa certa. Já serve para validar
        # se o PDF foi corretamente lido.

        # XXX: se um dia a pesquisa mudar a estrutura, estamos lascados

        # XXX: desativei esse teste, porque a pymupdf tem um bug, está retornando
        # um caractere inválido. https://github.com/pymupdf/PyMuPDF/issues/2876
        # self.assertEqual(parser.survey_title, "Pesquisa de Preços - Combustíveis")
        self.assertEqual(parser.data_pesquisa, "Realizada no dia 14 de novembro de 2023")

    def test_get_parts_of_post(self):

        linha = ['69420', 'Posto Hipotético\nR. XYZ, 1399, Bairro', 'ALFA', '100', '101', '102', '103', '104']
        partes = parser_core.separa_partes(linha)
        self.assertEqual(partes["id"], 69420)
        self.assertEqual(partes["nome"], "Posto Hipotético")
        self.assertEqual(partes["endereço"], "R. XYZ, 1399")
        self.assertEqual(partes["bairro"], "Bairro")
        self.assertEqual(partes["distribuidora"], "ALFA")
        self.assertEqual(partes["comum"], 100)
        self.assertEqual(partes["aditivada"], 101)
        self.assertEqual(partes["diesel"], 102)
        self.assertEqual(partes["etanol"], 103)
        self.assertEqual(partes["gnv"], 104)

    # Eu realmente gostaria de pegar a pessoa na prefeitura que gera essa planilha
    # e ter um papo sério com ela. Graças a ela, eu estou tendo que tratar um monte
    # de exceções.

    def test_nao_tem_bairro(self):
        linha = ['69420', 'Posto XPTO\nR. XYZ, 1234', 'ALFA', '100', '101', '102', '103', '104']
        partes = parser_core.separa_partes(linha)
        self.assertEqual(partes["id"], 69420)
        self.assertEqual(partes["nome"], "Posto XPTO")
        self.assertEqual(partes["endereço"], "R. XYZ, 1234")
        self.assertEqual(partes["bairro"], None)
        self.assertEqual(partes["distribuidora"], "ALFA")
        self.assertEqual(partes["comum"], 100)
        self.assertEqual(partes["aditivada"], 101)
        self.assertEqual(partes["diesel"], 102)
        self.assertEqual(partes["etanol"], 103)
        self.assertEqual(partes["gnv"], 104)


    # Tratar o caso do posto não vender um dos combustíveis
    def test_nao_vende_GNV(self):
        linha = ['69420', 'Posto Hipotético\nR. XYZ, 1399, Bairro', 'ALFA', '100', '101', '102', '103', '-']
        partes = parser_core.separa_partes(linha)
        self.assertEqual(partes["gnv"], None)

    def test_get_posts(self):
        parser = parser_core.PDFParser(self.target)
        self.assertEqual(parser.total_postos, 99)

    def test_mini_date_parser(self):
        # para não termos que arrastar uma biblioteca inteira para cá, vamos
        # escrever um "mini parser" para datas, que receba 
        # 'dia do mês de ano' e entregue 'dia/mês/ano'

        # O None é para podermos usar o número do mês como índice.
        
        data = "31 de Janeiro de 2024"
        self.assertEqual(parser_core.mini_date_parser(data), "31/01/2024")

        data = "31 de Outubro de 2024"
        self.assertEqual(parser_core.mini_date_parser(data), "31/10/2024")

        data = "Realizada no dia 31 de Dezembro de 2023"
        self.assertEqual(parser_core.mini_date_parser(data), "31/12/2023")
        
if __name__ == '__main__':
    unittest.main()
