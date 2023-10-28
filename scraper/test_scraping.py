import unittest, sys

sys.path.append('..')

import scraper 

class TestScrap(unittest.TestCase):
    result = None

    def test_can_get_of_URL(self):
        """ Verificar que conseguimos chegar no site da prefeitura e obter a página onde estão os links para os PDF. """
        self.result = scraper.get_content_of_URL(scraper.goal_URL('2023'))
        self.assertEqual(self.result.status_code, 200)
    
    def test_can_get_PDF_links(self):
        """ Verificar que conseguimos pegar os links do site anteriormente baixado. """
        self.result = scraper.get_PDFs_of_URL(scraper.goal_URL('2023'))
        for link in self.result:
            self.assertEqual(link.endswith('.pdf'), True)

if __name__ == '__main__':
    unittest.main()
