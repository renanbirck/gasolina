#!/usr/bin/env python3

import fitz 
import logging
from database import Database
logging.basicConfig(level=logging.DEBUG)

def flatten_list(xss):
    """ "achata" uma lista, isto é, [[1,2,3], [4,5,6]] vira [1,2,3,4,5,6]. 
        Simplifica a lógica do código. """
    return [x for xs in xss for x in xs]

def pretty_print_table(table):
    for line, text in enumerate(table):
        print(f"Linha {line}: {text}")

def separa_partes(linha):
    posto = {}
    try:
        posto["id"] = int(linha[0])
    except:
        raise ValueError("A linha não tem um ID válido!")
    
    # "Posto XPTO\nR. XYZ, 139, Bairro" -> ["Posto XPTO", "R. XYZ, 139", "Bairro"]

    partes_endereco = linha[1].split('\n')
    posto["nome"] = partes_endereco[0]

    endereco_bairro = partes_endereco[1:][0].split(",")
    posto["endereço"] = ','.join(endereco_bairro[:-1])
    posto["bairro"] = endereco_bairro[-1].strip()

    posto["distribuidora"] = linha[2]

    campos = ["comum", "aditivada", "diesel", "etanol", "gnv"]
    posto.update(zip(campos, [(float(preco.replace(',','.')) if '-' not in preco else None) for preco in linha[3:]]))
    
    return posto 
                
class PDFParser:

    file_name = None
    document = None
    
    data_pesquisa = None
    extracted = []

    database = Database()

    postos = []
  
    def __init__(self, file_name=None):
        if not file_name:
            raise ValueError("Você precisa informar um nome de arquivo!")
        self.file_name = file_name
        self.parse_PDF()

    def parse_PDF(self):
        logging.info(f"Processando o PDF {self.file_name}.")
        self.document = fitz.open(self.file_name)

        self.extract_tables()
        self.data_pesquisa = self.extracted[1][1]

        self.procura_postos()

    def extract_tables(self):
        for page in self.document: 
            page_tables = page.find_tables() # Procurar as tabelas
            if page_tables == []:  # Não tem?
                pass
            
            tab_contents = page_tables[0].extract()
            self.extracted.extend(tab_contents)

        logging.info(f"Achei {len(self.extracted)} linhas.")

    def procura_postos(self):
        """ Usa as funções da pymupdf para identificar a tabela onde estão as informações dos postos. 
            Muito mais elegante do que tentar fazer na mão. """
        # Todos os postos começam com um número, então, 
        # se a gente conseguir converter para inteiro, estamos no caminho certo.
        self.postos = []

        for line, content in enumerate(self.extracted):
           try:
            posto = separa_partes(content)
            logging.info(f"Achei um posto: {posto}")
            self.postos.append(posto)
           except:
            logging.info(f"Não parece um posto: {content}")
        
        self.total_postos = max([x["id"] for x in self.postos])

        pretty_print_table(self.postos)
        