#!/usr/bin/env python3
# Uma forma mais prática de testar o "parser".

import logging
from sys import argv, exit
from parser_core import PDFParser

if len(argv) < 2:
    exit("Você precisa informar um nome de arquivo!")

nome_arquivo = argv[1]

try:
    parser = PDFParser(nome_arquivo)
    parser.carrega_no_DB()
except Exception as e:
    logging.error(f"Falha ao processar {nome_arquivo}: {e}")
    exit(1)
