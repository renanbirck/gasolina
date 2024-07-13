#!/usr/bin/env python3

from sqlite3 import IntegrityError
import fitz 
import logging
from database import Database
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

    return f"{dia}/{('0' if numero_mes < 10 else '') + str(numero_mes)}/{ano}"

def separa_partes(linha):
    print(f">>> {linha}")

    posto = {}
    try:
        posto["id"] = int(linha[0])
    except:
        raise ValueError("A linha não tem um ID válido!")

    # "Posto XPTO\nR. XYZ, 139, Bairro" -> ["Posto XPTO", "R. XYZ, 139", "Bairro"]
    # "Posto XPTO\nR. XYZ, 139" -> ["Posto XPTO", "R. XYZ, 139", None]

    partes_endereco = linha[1].split('\n')
    posto["nome"] = partes_endereco[0]

    endereco_bairro = partes_endereco[1:][0].split(",")

    posto["endereço"] = ','.join(endereco_bairro[:-1])
    posto["bairro"] = endereco_bairro[-1].strip()

    posto["distribuidora"] = linha[2]

    campos = ["comum", "aditivada", "diesel", "etanol", "gnv"]
    posto.update(zip(campos, [(float(preco.replace(',','.')) if '-' not in preco else None) for preco in linha[3:]]))
   
    # XXX: Gambiarra para desfazer quando a prefeitura não colocou bairro.

    try:
        temp_numero = int(posto["bairro"])
        print(f"??? O posto {posto["id"]} tem número no lugar do bairro? Vamos fazer uma adaptação.")
        posto["bairro"] = None
        posto["endereço"] = posto["endereço"] + ', ' + str(temp_numero)

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

        data_pesquisa = mini_date_parser(self.data_pesquisa)

        try:
            self.database.cursor.execute("INSERT INTO Pesquisas(DataPesquisa) VALUES (?)", (data_pesquisa,))
        except:
            logging.error(f"A pesquisa de {data_pesquisa} já existe. Nada para fazer!")
            return 

        logging.info(f"Primeira passagem: carregando as distribuidoras...")
        for posto in self.postos:
            try:
                self.database.cursor.execute("INSERT INTO Distribuidoras(NomeDistribuidora) VALUES(?)", (posto["distribuidora"],))
            except: # Se cair aqui, é porque UNIQUE falhou. Não é um erro.
                logging.warning(f"A distribuidora {posto['distribuidora']} já existe (não tem nada de errado nisso).")

        self.database.cursor.execute("SELECT COUNT(IdDistribuidora) FROM Distribuidoras")
        logging.info(f"Cadastrei {self.database.cursor.fetchone()[0]} distribuidoras.")

        logging.info(f"Segunda passagem: carregando os postos...")
        for posto in self.postos:
            logging.info(f"Posto {posto['id']} de {self.total_postos}: {posto['nome']}...")
            try:
                self.database.cursor.execute("INSERT INTO PostosGasolina(IdPosto, IdDistribuidora, NomePosto, EnderecoPosto, BairroPosto) \
                                              VALUES(?,(SELECT IdDistribuidora FROM Distribuidoras WHERE NomeDistribuidora=(?)), ?, ?, ?)",
                                              (posto["id"], posto["distribuidora"], posto["nome"], posto["endereço"], posto["bairro"],))
            except:
                logging.warning(f"O posto {posto['id'], posto["nome"]} já está cadastrado (não tem nada de errado nisso, mas é bom revisar a tabela depois)")
        self.database.cursor.execute("SELECT COUNT(IdPosto) FROM PostosGasolina")
        logging.info(f"Cadastrei {self.database.cursor.fetchone()[0]} postos.")

        # Adicionar as pesquisas
