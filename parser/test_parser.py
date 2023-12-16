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

        # XXX: se um dia a pesquisa mudar a estrutura, estamos lascados

        # XXX: desativei esse teste, porque a pymupdf tem um bug, está retornando
        # um caractere inválido. https://github.com/pymupdf/PyMuPDF/issues/2876
        # self.assertEqual(parser.survey_title, "Pesquisa de Preços - Combustíveis")
        self.assertEqual(parser.survey_date, "Realizada no dia 14 de novembro de 2023")

if __name__ == '__main__':
    unittest.main()
