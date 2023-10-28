#!/usr/bin/env python3

import logging, requests
from bs4 import BeautifulSoup

goal_URL = lambda year: f"https://www.joinville.sc.gov.br/publicacoes/pesquisas-de-precos-combustiveis-{year}"

def get_content_to_URL(url: str):
    pass
