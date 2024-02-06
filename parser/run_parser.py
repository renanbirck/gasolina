#!/usr/bin/env python3
# Uma forma mais prática de testar o "parser".

from sys import argv 
from parser_core import PDFParser 

nome_arquivo = argv[1]

parser = PDFParser(nome_arquivo)
