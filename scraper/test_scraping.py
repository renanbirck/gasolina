import unittest, sys

sys.path.append('..')

import scraper 

class TestScrap(unittest.TestCase):
    def test_can_get_to_URL(self):
        """ Verificar que conseguimos chegar no site da prefeitura e obter a página onde estão os links para os PDF. """
        result = scraper.get_content_to_URL(scraper.goal_URL('2023'))
        self.assertEqual(result.status_code, 200)
         
if __name__ == '__main__':
    unittest.main()
