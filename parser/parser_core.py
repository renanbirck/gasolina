#!/usr/bin/env python3

import fitz 
import logging
from database import Database
logging.basicConfig(level=logging.DEBUG)

def flatten_list(xss):
    """ "achata" uma lista, isto é, [[1,2,3], [4,5,6]] vira [1,2,3,4,5,6]. 
        Simplifica a lógica do código. """
    return [x for xs in xss for x in xs]

def separa_partes(linha):
    posto = {}
    posto["id"] = int(linha[0])
    
    # "Posto XPTO\nR. XYZ, 139, Bairro" -> ["Posto XPTO", "R. XYZ, 139", "Bairro"]

    partes_endereco = linha[1].split('\n')
    print(partes_endereco)
    posto["nome"] = partes_endereco[0]

    endereco_bairro = partes_endereco[1:][0].split(",")
    posto["endereço"] = ','.join(endereco_bairro[:-1])
    posto["bairro"] = endereco_bairro[-1].strip()

    posto["distribuidora"] = linha[2]

    campos = ["comum", "aditivada", "diesel", "etanol", "gnv"]
    posto.update(zip(campos, [(float(preco) if '-' not in preco else None) for preco in linha[3:]]))
    
    return posto 
                
class PDFParser:

    file_name = None
    document = None
    
    data_pesquisa = None
    extracted = []

    database = Database()

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
        #self.pretty_print_table(self.extracted)

    def pretty_print_table(self, table):
        for line, text in enumerate(table):
            print(f"Linha {line}: {text}")

    def procura_postos(self):
        """ Usa as funções da pymupdf para identificar a tabela onde estão as informações dos postos. 
            Muito mais elegante do que tentar fazer na mão. """
        # Todos os postos começam com um número, então, 
        # se a gente conseguir converter para inteiro, estamos no caminho certo.

        for line, content in enumerate(self.extracted):
            try:
                id_posto = int(content[0])
                logging.info(f"Encontrei um posto! {content}")
            except(ValueError):
                logging.info(f"A linha {content} não me parece um posto.")
    
