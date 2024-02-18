#!/usr/bin/env python3
import scraper_core 
import logging 
from sys import argv

logging.basicConfig(level=logging.DEBUG)

def scrap():
    try:
        YEAR = str(argv[1])
    except:
        raise ValueError("Por favor informar um ano de PDFs para baixar!")

    URL = scraper_core.goal_URL(YEAR)
    PDFs = scraper_core.get_PDFs_of_URL(URL)

    for PDF in PDFs:
        logging.info(f"Baixando o arquivo {PDF}.")
        scraper_core.download_file(PDF)

if __name__ == '__main__':
    scrap()
