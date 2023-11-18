#!/usr/bin/env python3

import pypdfium2 as pdfium 
import logging
logging.basicConfig(level=logging.DEBUG)

class PDFProcessor:

    file_name = None
    pages = None
    content = None
    survey_title = "xxx"

    def __init__(self, file_name=None):
        if not file_name:
            raise ValueError("Você precisa informar um nome de arquivo!")
        self.file_name = file_name
        self.process_PDF()

    def process_PDF(self):
        print("entrei aqui")
        logging.info(f"Processando o PDF {self.file_name}.")
        self.pages = pdfium.PdfDocument(self.file_name)
        logging.info(f"Conseguimos! Ele tem {len(self.pages)} páginas.")
        self.survey_title = self.pages[0].get_textpage().get_text_range().split("\r\n")[0] # eca

