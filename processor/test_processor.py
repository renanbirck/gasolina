import unittest, sys
sys.path.append('..')

import processor_core

class TestProcessor(unittest.TestCase):
    processor = None
    def test_can_get_PDF(self):
        target = 'references/Novembro-2023.pdf'
        processor = processor_core.PDFProcessor(target)

        # Se tivermos conseguido ler o PDF, alguma coisa vai estar em 'pages'.
        self.assertNotEqual(processor.pages, None)

        # Se um dia começar a falhar aqui... talvez o PDF não tenha mais 4 páginas,
        # porque foram adicionados novos postos.
        self.assertEqual(len(processor.pages), 4)
