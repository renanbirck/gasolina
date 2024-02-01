#!/usr/bin/env python3

import fitz 
import logging
from database import Database
logging.basicConfig(level=logging.DEBUG)

def flatten_list(xss):
    """ "achata" uma lista, isto é, [[1,2,3], [4,5,6]] vira [1,2,3,4,5,6]. 
        Simplifica a lógica do código. """
    return [x for xs in xss for x in xs]

class PDFParser:

    file_name = None
    content = None
    titulo_pesquisa = "xxx"
    postos = []
    total_postos = 0
    distribuidoras = []
    database = Database()

    def __init__(self, file_name=None):
        if not file_name:
            raise ValueError("Você precisa informar um nome de arquivo!")
        self.file_name = file_name
        self.parse_PDF()

    def parse_PDF(self):
        logging.info(f"Processando o PDF {self.file_name}.")
        document = fitz.open(self.file_name)

        self.content = flatten_list([page.get_text().split('\n') for page in document])
        self.titulo_pesquisa, self.data_pesquisa = self.content[0], self.content[1]

        self.try_to_find_posts()

    def try_to_find_posts(self):
        """ Tentar inferir os postos de gasolina e suas informações.
            Numa função posterior, iremos identificar cada posto e os preços da tabela. """
        
        # TODO: ver se é possível simplificar essa lógica
        palavras_chave_nome = ["Posto", "Com. Comb", "Auto"]
        combustiveis = ["GASOLINA", "COMUM", "ADITIVADA", "DIESEL", "ETANOL", "GNV"]
        ignorar_palavras = ["BANDEIRA", "POSTO / ENDEREÇO", "PREÇO", "R$"]
        for num_linha, linha in enumerate(self.content):
            if any(name_keyword in linha for name_keyword in palavras_chave_nome):
                endereco_posto = self.content[num_linha + 1]
                logging.info(f"Achei o que parece ser o nome do posto {self.total_postos+1}, na linha {num_linha+1}: {linha}.")
                logging.info(f"O endereço desse posto é {endereco_posto}.")
                # Processar o endereço do posto. 
                # se algum CORNO na prefeitura decidir que bairro pode ter vírgula no nome,
                # eu faço questão de pegar o CORNO e apertar pelo pescoço até ele
                # se arrepender da decisão
                
                endereco_posto = endereco_posto.split(", ")
                rua, numero, bairro = endereco_posto[0], endereco_posto[1:-1], endereco_posto[-1]
                self.total_postos += 1

            # Os nomes das distribuidoras são sempre em CAPS LOCK,
            # então nós vamos precisar de uma lógica para filtrar palavras em CAPS LOCK
            # que não sejam nomes de distribuidoras.

            elif linha.isupper() and not any(nome_combustivel in linha for nome_combustivel in combustiveis) \
                                and not any(palavra_a_ignorar in linha for palavra_a_ignorar in ignorar_palavras):
                logging.info(f"Nome da distribuidora: {linha}.")
                self.distribuidoras.append(linha)
            

        logging.info(f"Achei {self.total_postos} postos.")

        # Não tem por que uma distribuidora se repetir.
        self.distribuidoras = set(self.distribuidoras)
        self.load_into_database()
    
    def load_into_database(self):
            for distribuidora in self.distribuidoras:
                try:
                    self.database.cursor.execute("INSERT INTO Distribuidoras(NomeDistribuidora) VALUES(?)", (distribuidora, ))
                except:
                    logging.info(f"Nome de distribuidora repetido: {distribuidora}")