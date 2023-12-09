import unittest, sys
sys.path.append('..')

import parser_core
import datetime

class TestParser(unittest.TestCase):

    target = 'references/Novembro-2023.pdf'

    def test_can_get_PDF(self):
        parser = parser_core.PDFParser(self.target)

        # Se tivermos conseguido ler o PDF, alguma coisa vai estar em 'pages'.
        self.assertNotEqual(parser.pages, None)

        # Se um dia começar a falhar aqui... talvez o PDF não tenha mais 4 páginas,
        # porque foram adicionados novos postos.
        self.assertEqual(len(parser.pages), 4)

    def test_can_get_survey_info(self):

        parser = parser_core.PDFParser(self.target)
       
        # Testar se a gente está na pesquisa certa. Já serve para validar
        # se o PDF foi corretamente lido.

        self.assertEqual(parser.survey_title, "Pesquisa de Preços - Combustíveis")

if __name__ == '__main__':
    unittest.main()
