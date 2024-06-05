#!/usr/bin/env python3

# Script para teste, que importa um arquivo PDF de pesquisa 
# e gera um arquivo CSV. Usado principalmente para testar 
# algoritmos sem precisar de um BD.

import fitz, sys, csv 

try:
    doc = fitz.open(sys.argv[1])
except:
    raise ValueError("Por favor informar um nome de arquivo!")

column_names = None 
extracted = []

for page in doc:        # A cada página do PDF,
    page_tables = page.find_tables()  # procurar as tabelas.
    if page_tables.tables == []:  # Não tem tabela? Segue em frente.
        pass

    tab = page_tables [0]
    header = tab.header
    external = header.external
    names = header.names
    if page.number == 0:  # Se for a primeira página, pegar o nome das colunas 
        column_names = names
    extract = tab.extract()
    extracted.extend(extract)

print(f"Encontrei {len(extracted)} linhas e {len(column_names)} colunas.")

for line, text in enumerate(extracted):
    print(text)
    # OK, temos os dados: vamos mastigar para algo que possa ser convertido para CSV.

    try:
        num_posto = int(text[0])
    except:
        if '202' in text[1]:
            print(f"{text[1]}")
        print(f"Linha {line} não é um posto, pulando ela...")
