import unittest, sys
sys.path.append('..')

import parser_core
import datetime

class TestParser(unittest.TestCase):

    target = 'references/Novembro-2023.pdf'

    def test_can_get_PDF(self):
        parser = parser_core.PDFParser(self.target)
        # Se tivermos conseguido ler o PDF, alguma coisa vai estar em 'pages'.
        self.assertNotEqual(parser.document, None)


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

    def test_get_posts(self):
        parser = parser_core.PDFParser(self.target)
        self.assertEqual(parser.total_postos, 99)


if __name__ == '__main__':
    unittest.main()
