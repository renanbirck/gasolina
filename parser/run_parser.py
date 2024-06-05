#!/usr/bin/env python3
# Uma forma mais prática de testar o "parser".

from sys import argv 
from parser_core import PDFParser 

try:
    nome_arquivo = argv[1]
except:
    raise ValueError("Você precisa informar um nome de arquivo!")

parser = PDFParser(nome_arquivo)
