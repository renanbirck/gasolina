#!/usr/bin/env python3
# Uma forma mais prática de testar o "parser".

from sys import argv 
from parser_core import PDFParser 

nome_arquivo = argv[1]

try:
    parser = PDFParser(nome_arquivo)
except:
    print(f"Epa! Não consegui ler o arquivo {nome_arquivo}!")