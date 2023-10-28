#!/usr/bin/env python3

import logging, requests
logging.basicConfig(level=logging.DEBUG)
from bs4 import BeautifulSoup

goal_URL = lambda year: f"https://www.joinville.sc.gov.br/publicacoes/pesquisas-de-precos-combustiveis-{year}"

def get_content_to_URL(url: str):
    logging.info(f'Acessando a URL: {url}')
    url_data = requests.get(url)
    logging.info(f'Status HTTP: {url_data.status_code}')
    return url_data
