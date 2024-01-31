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
        """ Tentar inferir os postos de gasolina e suas informações.
            Numa função posterior, iremos identificar cada posto e os preços da tabela. """

        name_keywords = ["Posto", "Com. Comb", "Auto"]
        fuel_names = ["GASOLINA", "COMUM", "ADITIVADA", "DIESEL", "ETANOL", "GNV"]
        unwanted_keywords = ["BANDEIRA", "POSTO / ENDEREÇO", "PREÇO", "R$"]
        for line_number, line in enumerate(self.content):
            if any(name_keyword in line for name_keyword in name_keywords):
                address = self.content[line_number + 1]
                logging.info(f"Achei o que parece ser o nome do posto {self.number_of_posts+1}, na linha {line_number+1}: {line}.")
                logging.info(f"O endereço desse posto é {address}.")
                # Processar o endereço do posto. 
                # se algum CORNO na prefeitura decidir que bairro pode ter vírgula no nome,
                # eu faço questão de pegar o CORNO e apertar pelo pescoço até ele
                # se arrepender da decisão
                
                address = address.split(", ")
                street, number, neighbourhood = address[0], address[1:-1], address[-1]
                self.number_of_posts += 1
            # Os nomes das distribuidoras são sempre em CAPS LOCK,
            # então nós vamos precisar de uma lógica para filtrar palavras em CAPS LOCK
            # que não sejam nomes de distribuidoras.

            # XXX: puta que pariu, esse é o código mais HEDIONDO que eu já cometi na minha vida.
            # Ver se tem alguma forma de limpar.

            elif line.isupper() and not any(fuel_name in line for fuel_name in fuel_names) and not any(unwanted_keyword in line for unwanted_keyword in unwanted_keywords):
                logging.info(f"Nome da distribuidora: {line}.")
                
        logging.info(f"Achei {self.number_of_posts} postos.")
                
