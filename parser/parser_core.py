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

    dados_postos = {}  

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
        self.load_into_table()

    def try_to_find_posts(self):
        """ Tentar inferir os postos de gasolina e suas informações.
            Numa função posterior, iremos identificar cada posto e os preços da tabela. """
        
        # TODO: ver se é possível simplificar essa lógica
        palavras_chave_nome = ["Posto", "Com. Comb", "Auto"]
        combustiveis = ["GASOLINA", "COMUM", "ADITIVADA", "DIESEL", "ETANOL", "GNV"]
        ignorar_palavras = ["BANDEIRA", "POSTO / ENDEREÇO", "PREÇO", "R$"]
        rua = None

        for num_linha, linha in enumerate(self.content):
            if any(palavra_chave in linha for palavra_chave in palavras_chave_nome):
                nome_posto = self.content[num_linha]
                endereco_posto = self.content[num_linha + 1]
                logging.info(f"Achei o que parece ser o nome do posto {self.total_postos+1}, na linha {num_linha+1}: {linha}.")
                logging.info(f"O endereço desse posto é {endereco_posto}.")
                # Processar o endereço do posto. 
                # se algum CORNO na prefeitura decidir que bairro pode ter vírgula no nome,
                # eu faço questão de pegar o CORNO e apertar pelo pescoço até ele
                # se arrepender da decisão
                
                endereco_posto = endereco_posto.strip().split(", ")
                rua, bairro = ', '.join(endereco_posto[0:-1]), endereco_posto[-1]
                self.total_postos += 1

            # Os nomes das distribuidoras são sempre em CAPS LOCK,
            # então nós vamos precisar de uma lógica para filtrar palavras em CAPS LOCK
            # que não sejam nomes de distribuidoras.

            elif linha.isupper() and not any(nome_combustivel in linha for nome_combustivel in combustiveis) \
                                and not any(palavra_a_ignorar in linha for palavra_a_ignorar in ignorar_palavras):
                distribuidora_atual = linha
                logging.info(f"Nome da distribuidora: {distribuidora_atual}.")
        
            if rua:  # Se continuar em none, sabemos que não era um posto
                self.dados_postos[self.total_postos] = [nome_posto, rua, bairro, distribuidora_atual]
            
        logging.info(f"Achei {self.total_postos} postos.")
        print(self.dados_postos)

    def load_into_table(self):
        # Primeiro, alimentar a tabela com as bandeiras.

        distribuidoras = [posto[-1] for posto in self.dados_postos.values()]
        for distribuidora in distribuidoras:
            try:
                self.database.cursor.execute("INSERT INTO Distribuidoras(NomeDistribuidora) VALUES (?)", distribuidora)
            except: # Falhou a restrição UNIQUE (não tem nada de errado nisso)
                logging.info(f"Opa, a distribuidora {distribuidora} já existe (não tem nada de errado nisso).")

        # Depois, adicionar os postos. Isso parte da premissa que um posto
        # nunca vai mudar de bandeira (acredito que isso seja raro o suficiente).
