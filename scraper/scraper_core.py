#!/usr/bin/env python3

import logging, requests
logging.basicConfig(level=logging.INFO)
from bs4 import BeautifulSoup
from os import makedirs, replace
from os.path import isfile, getsize, join
from urllib.parse import urljoin, urlparse, unquote

goal_URL = lambda year: f"https://www.joinville.sc.gov.br/publicacoes/pesquisas-de-precos-combustiveis-{year}"

TIMEOUT = 60  # segundos; sem isso, uma conexão travada deixa o scraper parado para sempre

# Uma sessão reaproveita a conexão com o servidor da prefeitura entre os downloads.
session = requests.Session()

def get_content_of_URL(url: str):
    """ Puxa o conteúdo da URL informada. """

    logging.info(f'Acessando a URL: {url}')
    url_data = session.get(url, timeout=TIMEOUT)
    logging.info(f'Status HTTP: {url_data.status_code}')
    url_data.raise_for_status()
    return url_data

def get_PDFs_of_URL(url: str):
    links = []
    soup = BeautifulSoup(get_content_of_URL(url).content, "html5lib")
    for link in soup.find_all('a', href=True):
        # Links relativos são resolvidos a partir da página.
        href = urljoin(url, str(link['href']))
        if urlparse(href).path.lower().endswith('.pdf') and href not in links:
            logging.info(f"Encontramos um link para um PDF! {href}")
            links.append(href)
    logging.info(f"Encontrei os links: {links}")
    return links

def download_file(url: str, subdirectory: str = 'data'):
    """ Baixa o arquivo especificado, colocando ele no diretório informado em subdirectory.
        Arquivos que já foram baixados são pulados. """
    makedirs(subdirectory, exist_ok=True)

    # Determinar e compor o nome do arquivo.
    end_name = unquote(urlparse(url).path.rsplit('/', 1)[1])
    final_file_name = join(subdirectory, end_name)

    logging.info(f"O nome do arquivo será {final_file_name}.")

    if isfile(final_file_name) and getsize(final_file_name) > 0:
        logging.info(f"O arquivo {final_file_name} já existe, não vou baixar de novo.")
        return final_file_name

    downloaded = session.get(url, allow_redirects=True, timeout=TIMEOUT)
    downloaded.raise_for_status()

    # Às vezes o servidor devolve uma página HTML de erro com status 200.
    if not downloaded.content.startswith(b'%PDF'):
        raise ValueError(f"O conteúdo de {url} não é um PDF!")

    # Grava em um arquivo temporário e renomeia, para nunca ficar um PDF pela metade.
    temp_file_name = final_file_name + '.part'
    with open(temp_file_name, 'wb') as f:
        f.write(downloaded.content)
    replace(temp_file_name, final_file_name)

    return final_file_name
