#!/usr/bin/env python3

import fitz 
import logging
logging.basicConfig(level=logging.DEBUG)


class PDFParser:

    file_name = None
    pages = None
    content = None
    survey_title = "xxx"

    def __init__(self, file_name=None):
        if not file_name:
            raise ValueError("Você precisa informar um nome de arquivo!")
        self.file_name = file_name
        self.parse_PDF()

    def get_text_of_page(self, number):
        """ Retorna o texto da página 'number' (obs. a primeira página do PDF é zero)
            já separado em linhas. """

        return self.pages[number].get_text().split('\n')

    def parse_PDF(self):
        logging.info(f"Processando o PDF {self.file_name}.")
        self.pages = fitz.open(self.file_name)
        self.survey_title = self.get_text_of_page(0)[0]
        self.survey_date = self.get_text_of_page(0)[1]