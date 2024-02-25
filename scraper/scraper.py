#!/usr/bin/env python3
import scraper_core, logging 
from sys import argv
from datetime import date

logging.basicConfig(level=logging.DEBUG)

def scrap():
    try:
        YEAR = str(argv[1])
    except:
        YEAR = date.today().strftime("%Y")
        logging.info(f"Não fui informado um ano... presumindo que é o ano de {YEAR}.")

    URL = scraper_core.goal_URL(YEAR)
    PDFs = scraper_core.get_PDFs_of_URL(URL)

    for PDF in PDFs:
        logging.info(f"Baixando o arquivo {PDF}.")
        scraper_core.download_file(PDF)

if __name__ == '__main__':
    scrap()
