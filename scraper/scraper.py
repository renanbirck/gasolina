#!/usr/bin/env python3
import scraper_core, logging
from sys import argv, exit
from datetime import date

logging.basicConfig(level=logging.INFO)

def scrap():
    if len(argv) > 1:
        YEAR = str(argv[1])
    else:
        YEAR = date.today().strftime("%Y")
        logging.info(f"Não fui informado um ano... presumindo que é o ano de {YEAR}.")

    URL = scraper_core.goal_URL(YEAR)
    PDFs = scraper_core.get_PDFs_of_URL(URL)

    # Um download com problema não impede os outros, mas o código de saída indica a falha.
    falhas = 0
    for PDF in PDFs:
        logging.info(f"Baixando o arquivo {PDF}.")
        try:
            scraper_core.download_file(PDF)
        except Exception as e:
            logging.error(f"Falha ao baixar {PDF}: {e}")
            falhas += 1

    return falhas

if __name__ == '__main__':
    exit(1 if scrap() else 0)
