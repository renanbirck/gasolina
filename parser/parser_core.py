#!/usr/bin/env python3

import fitz 
import logging
logging.basicConfig(level=logging.DEBUG)

def flatten_list(xss):
    """ "achata" uma lista, isto é, [[1,2,3], [4,5,6]] vira [1,2,3,4,5,6]. 
        Simplifica a lógica do código. """
    return [x for xs in xss for x in xs]

class PDFParser:

    file_name = None
    content = None
    survey_title = "xxx"
    posts = []
    number_of_posts = 0

    def __init__(self, file_name=None):
        if not file_name:
            raise ValueError("Você precisa informar um nome de arquivo!")
        self.file_name = file_name
        self.parse_PDF()

    def parse_PDF(self):
        logging.info(f"Processando o PDF {self.file_name}.")
        document = fitz.open(self.file_name)
        self.pages = flatten_list([page.get_text().split('\n') for page in document])
        self.survey_title, self.survey_date = self.pages[0], self.pages[1]


    def try_to_find_posts(self):
        """ Tentar inferir os postos de gasolina e seus endereços. """
