#!/usr/bin/env python3
import scraper_core 
import logging 

logging.basicConfig(level=logging.DEBUG)

def scrap():
    YEAR = "2023"  # ano para o qual queremos baixar os PDFs (sim, é string mesmo)

    URL = scraper_core.goal_URL(YEAR)
    PDFs = scraper_core.get_PDFs_of_URL(URL)

    for PDF in PDFs:
        logging.info(f"Baixando o arquivo {PDF}.")
        scraper_core.download_file(PDF)

if __name__ == '__main__':
    scrap()
