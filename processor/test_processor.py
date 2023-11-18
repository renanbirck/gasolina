import unittest, sys
sys.path.append('..')

import processor_core
import datetime

class TestProcessor(unittest.TestCase):

    target = 'references/Novembro-2023.pdf'

    def test_can_get_PDF(self):
        processor = processor_core.PDFProcessor(self.target)

        # Se tivermos conseguido ler o PDF, alguma coisa vai estar em 'pages'.
        self.assertNotEqual(processor.pages, None)

        # Se um dia começar a falhar aqui... talvez o PDF não tenha mais 4 páginas,
        # porque foram adicionados novos postos.
        self.assertEqual(len(processor.pages), 4)

    def test_can_get_survey_info(self):

        processor = processor_core.PDFProcessor(self.target)
       
        # Testar se a gente está na pesquisa certa.
        self.assertEqual(processor.survey_title, "Pesquisa de Preços - Combustíveis")

if __name__ == '__main__':
    unittest.main()
