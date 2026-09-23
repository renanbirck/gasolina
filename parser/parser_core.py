#!/usr/bin/env python3

import fitz
import logging
import re
import requests
from datetime import datetime
from os import environ

logging.basicConfig(level=logging.INFO)

# Símbolos (ligaduras) que apareceram dentro do PDF, e o que eles deveriam ser.
LIGADURAS = {'Ʃ': 'tt', 'Ɵ': 'ti'}

# A data da pesquisa aparece em uma célula do tipo "Realizada no dia 14 de novembro de 2023".
REGEX_DATA = re.compile(r"Realizada no dia\s+(\d{1,2})º?\s+de\s+(\w+)\s+de\s+(\d{4})", re.IGNORECASE)

def pretty_print_table(table):
    for line, text in enumerate(table):
        print(f"Linha {line}: {text}")

def mini_date_parser(date):
    # Um mini-parser para transformar datas do tipo 'XX de YY de ZZZZ' em 'ZZZZYYXX'.
    # Levanta ValueError se a data for inválida (ex.: '32 de fevereiro de 2024').

    meses = [None, "janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
                   "agosto", "setembro", "outubro", "novembro", "dezembro"]

    string_date = date.lower()

    parts = string_date.split()

    dia, _, mes, _, ano = parts[-5:]

    numero_mes = meses.index(mes)

    return datetime(int(ano), numero_mes, int(dia.rstrip('º'))).strftime("%Y%m%d")

def parse_preco(preco):
    # '6,29' -> 6.29; '-', '' ou None (o posto não vende o combustível) -> None
    if preco is None or '-' in preco or not preco.strip():
        return None
    return float(preco.replace('R$', '').replace(',', '.'))

def corrige_ligaduras(texto):
    for simbolo, correto in LIGADURAS.items():
        texto = texto.replace(simbolo, correto)
    return texto

def separa_partes(linha):

    # Se a linha começar com None seguido do ID (como aconteceu com o PDF de novembro/2024),
    # então a gente precisa de um "offset".
    precisa_offset = int(linha[0] is None and len(linha) > 1 and str(linha[1]).strip().isdigit())
    linha = linha[precisa_offset:]

    posto = {}
    try:
        posto["id"] = int(linha[0])
    except (TypeError, ValueError):
        raise ValueError("A linha não tem um ID válido!")

    # "Posto XPTO\nR. XYZ, 139, Bairro" -> ["Posto XPTO", "R. XYZ, 139", "Bairro"]
    # "Posto XPTO\nR. XYZ, 139" -> ["Posto XPTO", "R. XYZ, 139", None]

    partes_endereco = linha[1].split('\n')
    posto["nome"] = partes_endereco[0]

    endereco_bairro = partes_endereco[1].split(",")

    posto["endereco"] = ','.join(endereco_bairro[:-1])
    posto["bairro"] = endereco_bairro[-1].strip()

    # "kludge" para consertar símbolos que apareceram dentro do PDF

    for campo in ("nome", "bairro", "endereco"):
        posto[campo] = corrige_ligaduras(posto[campo])

    posto["distribuidora"] = linha[2]

    # Nos PDFs mais novos, a prefeitura colocou o campo para gasolina "premium". Então precisamos tratar aqui, adicionando mais um campo

    precos = [parse_preco(preco) for preco in linha[3:]]
    if len(linha) == 9:
        campos = ["comum", "aditivada", "premium", "diesel", "etanol", "gnv"]
    elif len(linha) == 8:
        campos = ["comum", "aditivada", "diesel", "etanol", "gnv"]
        posto['premium'] = None
    else:
        raise ValueError(f"A linha tem um número inesperado de colunas: {len(linha)}")
    posto.update(zip(campos, precos))

    # XXX: Gambiarra para desfazer quando a prefeitura não colocou bairro.

    if posto["bairro"].isdigit():
        print(f"??? O posto {posto["id"]} tem número no lugar do bairro? Vamos fazer uma adaptação.")
        posto["endereco"] = posto["endereco"] + ', ' + posto["bairro"]
        posto["bairro"] = None

    return posto

class PDFParser:

    def __init__(self, file_name=None):
        if not file_name:
            raise ValueError("Você precisa informar um nome de arquivo!")
        self.file_name = file_name
        self.data_pesquisa = None
        self.extracted = []
        self.postos = []
        self.parse_PDF()

    def parse_PDF(self):
        logging.info(f"Processando o PDF {self.file_name}.")
        self.document = fitz.open(self.file_name)

        self.extract_tables()
        self.data_pesquisa = self.procura_data()

        self.procura_postos()

    def extract_tables(self):
        for page in self.document:
            page_tables = page.find_tables() # Procurar as tabelas
            if not page_tables.tables:  # Não tem? Segue para a próxima página.
                continue

            tab_contents = page_tables[0].extract()
            self.extracted.extend(tab_contents)

        logging.info(f"Achei {len(self.extracted)} linhas.")

    def procura_data(self):
        """ Procura a célula com a data da pesquisa. A posição dela muda de um PDF
            para outro (em dezembro/2025 ela estava na primeira linha). """
        for linha in self.extracted:
            for celula in linha:
                if celula and (encontrada := REGEX_DATA.search(celula)):
                    return encontrada.group(0)
        raise ValueError(f"Não encontrei a data da pesquisa em {self.file_name}!")

    def procura_postos(self):
        """ Usa as funções da pymupdf para identificar a tabela onde estão as informações dos postos.
            Muito mais elegante do que tentar fazer na mão. """
        # Todos os postos começam com um número, então,
        # se a gente conseguir converter para inteiro, estamos no caminho certo.
        self.postos = []

        for content in self.extracted:
            try:
                posto = separa_partes(content)
                logging.debug(f"Achei um posto: {posto}")
                self.postos.append(posto)
            except (ValueError, IndexError, AttributeError) as e:
                # Uma linha que parece de posto (8 ou mais colunas, com nome e endereço)
                # mas não foi lida é dado perdido, então merece destaque.
                if len(content) >= 8 and '\n' in str(content[1]):
                    logging.warning(f"Linha que parece ser de um posto foi descartada ({e}): {content}")
                else:
                    logging.debug(f"Não parece um posto: {content}")

        if not self.postos:
            raise ValueError(f"Não encontrei nenhum posto em {self.file_name}!")

        self.total_postos = max(x["id"] for x in self.postos)
        logging.info(f"Achei {len(self.postos)} postos na pesquisa de {self.data_pesquisa}.")

    def carrega_no_DB(self):
        """ Envia a pesquisa para a API, que grava tudo em uma única transação. """
        API_BASE = environ.get("GASOLINA_API_BASE")
        if not API_BASE:
            logging.info("A variável de ambiente GASOLINA_API_BASE não está setada! Vou presumir que a API roda localmente.")
            API_BASE = 'http://127.0.0.1:8000'

        logging.info(f"A nossa API fica em {API_BASE}.")

        # As rotas de escrita da API exigem a chave.
        headers = {"X-API-Key": environ.get("GASOLINA_API_KEY", "")}

        importacao = {"data": mini_date_parser(self.data_pesquisa),
                      "postos": self.postos}

        result = requests.post(f"{API_BASE}/pesquisa/importar", json=importacao,
                               headers=headers, timeout=60)

        if result.status_code != 200:
            raise RuntimeError(f"Erro ao importar a pesquisa! {result.status_code} - {result.text}")

        logging.info(f"Pesquisa importada com sucesso: {result.json()}")
        return result.json()
