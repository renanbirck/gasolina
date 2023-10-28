#!/usr/bin/env python3

import logging, requests
logging.basicConfig(level=logging.DEBUG)
from bs4 import BeautifulSoup

goal_URL = lambda year: f"https://www.joinville.sc.gov.br/publicacoes/pesquisas-de-precos-combustiveis-{year}"

def get_content_of_URL(url: str):
    """ Puxa o conteúdo da URL informada. """

    logging.info(f'Acessando a URL: {url}')
    url_data = requests.get(url)
    logging.info(f'Status HTTP: {url_data.status_code}')
    return url_data

def get_PDFs_of_URL(url: str):
    links = []
    soup = BeautifulSoup(get_content_of_URL(url).content, "html5lib")
    for link in soup.find_all('a', href=True):
        if link['href'].endswith('.pdf'):
            logging.info(f"Encontramos um link para um PDF! {link['href']}")
            links.append(link['href'])
    logging.info(f"Encontrei os links: {links}")
    return links

