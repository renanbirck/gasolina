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
        self.content = flatten_list([page.get_text().split('\n') for page in document])
        self.survey_title, self.survey_date = self.content[0], self.content[1]

        self.try_to_find_posts()

    def try_to_find_posts(self):
        keywords = ["Posto", "Com. Comb", "Auto"]
        """ Tentar inferir os postos de gasolina e seus endereços. """
        for line_number, line in enumerate(self.content):
            if any(keyword in line for keyword in keywords):
                logging.info(f"Achei o que parece ser o nome do posto {self.number_of_posts+1}, na linha {line_number+1}: {line}.")
                self.number_of_posts += 1
        logging.info(f"Achei {self.number_of_posts} postos.")
                
