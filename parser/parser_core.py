#!/usr/bin/env python3

from sqlite3 import IntegrityError
import fitz 
import logging
from database import Database
import requests 

logging.basicConfig(level=logging.DEBUG)

def pretty_print_table(table):
    for line, text in enumerate(table):
        print(f"Linha {line}: {text}")

def mini_date_parser(date):
    # Um mini-parser para transformar datas do tipo 'XX de YY de ZZZZ' em 'XX/YY/ZZZZ'.
    # Intencionalmente não faz nenhuma verificação de erro, ou seja, se o usuário
    # especificar '32 de fevereiro de 3.1415', ele vai ter '32/02/3.1415'.

    meses = [None, "janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", 
                   "agosto", "setembro", "outubro", "novembro", "dezembro"]

    string_date = date.lower()

    parts = string_date.split(' ')
    
    dia, _, mes, _, ano = parts[-5:]
    
    numero_mes = meses.index(mes)

    return f"{ano}{'0' if numero_mes < 10 else ''}{str(numero_mes)}{dia}"
    #return f"{dia}/{('0' if numero_mes < 10 else '') + str(numero_mes)}/{ano}"

def separa_partes(linha):
    
    # Se a linha começar com None (como aconteceu com o PDF de novembro/2024), então a gente precisa de um "offset".
    # XXX: Seria interessante generalizar isso
    precisa_offset = (linha[0] == None)

    posto = {}
    try:
        posto["id"] = int(linha[0 + precisa_offset])
    except:
        raise ValueError("A linha não tem um ID válido!")

    # "Posto XPTO\nR. XYZ, 139, Bairro" -> ["Posto XPTO", "R. XYZ, 139", "Bairro"]
    # "Posto XPTO\nR. XYZ, 139" -> ["Posto XPTO", "R. XYZ, 139", None]

    partes_endereco = linha[1 + precisa_offset].split('\n')
    posto["nome"] = partes_endereco[0]

    endereco_bairro = partes_endereco[1:][0].split(",")

    posto["endereco"] = ','.join(endereco_bairro[:-1])
    posto["bairro"] = endereco_bairro[-1].strip()

    # "kludge" para consertar símbolos que apareceram dentro do PDF

    posto["nome"] = posto["nome"].replace('Ʃ', 'tt')
    posto["nome"] = posto["nome"].replace('Ɵ', 'ti')

    posto["bairro"] = posto["bairro"].replace('Ʃ', 'tt')
    posto["bairro"] = posto["bairro"].replace('Ɵ', 'ti')

    posto["endereco"] = posto["endereco"].replace('Ɵ', 'ti')
    posto["endereco"] = posto["endereco"].replace('Ʃ', 'tt')

    posto["distribuidora"] = linha[2 + precisa_offset]

    # Nos PDFs mais novos, a prefeitura colocou o campo para gasolina "premium". Então precisamos tratar aqui, adicionando mais um campo

    if len(linha) == 9:
        campos = ["comum", "aditivada", "premium", "diesel", "etanol", "gnv"]
        posto.update(zip(campos, [(float(preco.replace(',','.')) if '-' not in preco else None) for preco in linha[3 + precisa_offset:]]))
    else:
        campos = ["comum", "aditivada", "diesel", "etanol", "gnv"]
        posto.update(zip(campos, [(float(preco.replace(',','.')) if '-' not in preco else None) for preco in linha[3 + precisa_offset:]]))
        posto['premium'] = None

    # XXX: Gambiarra para desfazer quando a prefeitura não colocou bairro.

    try:
        temp_numero = int(posto["bairro"])
        print(f"??? O posto {posto["id"]} tem número no lugar do bairro? Vamos fazer uma adaptação.")
        posto["bairro"] = None
        posto["endereco"] = posto["endereco"] + ', ' + str(temp_numero)

    except: # int não deu certo, ou seja, não tem número no lugar do bairro
        pass

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

        for _, content in enumerate(self.extracted):
           try:
            posto = separa_partes(content)
            logging.info(f"Achei um posto: {posto}")
            self.postos.append(posto)
           except:
            logging.info(f"Não parece um posto: {content}")

        self.total_postos = max([x["id"] for x in self.postos])

        pretty_print_table(self.postos)

        self.carrega_no_DB()

    def carrega_no_DB(self):
        """ Carrega as informações que lemos anteriormente. """
        # TODO: colocar tudo na mesma etapa, para ganharmos tempo e simplificarmos o código.

        # API_BASE = 'http://localhost:8000'
        API_BASE = 'https://gasolina.renanbirck.rocks'

        data_pesquisa = mini_date_parser(self.data_pesquisa)

        # Criar nova pesquisa chamando a API 

        result = requests.post(f"{API_BASE}/pesquisa/nova", json={"data": data_pesquisa})

        if result.status_code != 200:
            logging.error(f"Erro ao criar pesquisa! {result.status_code} - {result.text}")
            return
        
        id_pesquisa = result.json()["id"]

        logging.info(f"Pesquisa criada com sucesso no id {id_pesquisa}! {result.json()}")
        
        logging.info(f"Carregando as distribuidoras...")
        for posto in self.postos:
            result = requests.post(f"{API_BASE}/distribuidora/nova", json={"nome": posto["distribuidora"]})
            if result.status_code != 200:   
                logging.warning(f"Distribuidora {posto['distribuidora']} já existe! (não tem nada de errado nisso)")
            else:
                logging.info(f"Distribuidora {posto['distribuidora']} cadastrada com sucesso!")
            
        logging.info(f"Carregando os postos...")
        for posto in self.postos:
            logging.info(f"Posto {posto['id']} de {self.total_postos}: {posto['nome']}...")
            result = requests.post(f"{API_BASE}/posto/novo", json=posto)
        
        # Adicionar os preços.
        logging.info(f"Terceira passagem: carregando os preços na pesquisa {id_pesquisa}...")

        for posto in self.postos:
            
            # Renomear as chaves para caberem no precoModel
            # TODO: alterar as chaves para evitar esse renomeio
            preco = {
                "pesquisa": id_pesquisa,
                "posto": posto["id"],
                "precoGasolinaComum": posto.get("comum"),
                "precoGasolinaAditivada": posto.get("aditivada"),
                "precoGasolinaPremium": posto.get("premium"),
                "precoEtanol": posto.get("etanol"),
                "precoDiesel": posto.get("diesel"),
                "precoGNV": posto.get("gnv"),
            }

            print(posto)

            result = requests.post(f"{API_BASE}/preco/novo", json=preco)
            if result.status_code != 200:
                logging.error(f"Erro ao adicionar preço do posto {posto['id']}! {result.status_code} - {result.text}")
            else:
                logging.info(f"Preço do posto {posto['id']} adicionado com sucesso!")

