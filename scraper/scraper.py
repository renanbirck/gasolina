#!/usr/bin/env python3

import logging, requests
logging.basicConfig(level=logging.DEBUG)
from bs4 import BeautifulSoup
from os import mkdir

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

def download_file(url: str, subdirectory: str):
    """ Baixa o arquivo especificado, colocando ele no diretório informado em subdirectory. """
    try:
        mkdir(subdirectory)
    except(FileExistsError):
        logging.warn(f"O diretório {subdirectory} já existe (não tem nada de errado nisso).")

    downloaded = requests.get(url, allow_redirects=True)

    # Determinar e compor o nome do arquivo.
    end_name = url.rsplit('/', 1)[1]
    final_file_name = subdirectory + '/' + end_name

    logging.info(f"O nome do arquivo será {final_file_name}.")

    with open(final_file_name, 'wb') as f:
        f.write(downloaded.content)
