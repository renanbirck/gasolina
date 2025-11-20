#!/usr/bin/env python3

# Script para teste, que importa um arquivo PDF de pesquisa
# e gera um arquivo CSV. Usado principalmente para testar
# algoritmos sem precisar de um BD.

import csv
import sys

import fitz

try:
    doc = fitz.open(sys.argv[1])
except:
    raise ValueError("Por favor informar um nome de arquivo!")

column_names = None
extracted = []

for page in doc:  # A cada página do PDF,
    page_tables = page.find_tables()  # procurar as tabelas.
    if page_tables.tables == []:  # Não tem tabela? Segue em frente.
        pass

    tab = page_tables[0]
    header = tab.header
    external = header.external
    names = header.names
    if page.number == 0:  # Se for a primeira página, pegar o nome das colunas
        column_names = names
    extract = tab.extract()
    extracted.extend(extract)

print(f"Encontrei {len(extracted)} linhas e {len(column_names)} colunas.")

for line, text in enumerate(extracted):

    def number_or_none(number, kind):
        """Tenta converter para kind, se não, retorna None"""
        if not number:
            return None
        try:
            return kind(number.replace(",", "."))
        except ValueError:  # Não é um número do tipo que a gente pediu (kind)
            return None

    line_contents = []

    # OK, temos os dados: vamos mastigar para algo que possa ser convertido para CSV.

    try:
        id_posto = number_or_none(text[0], int)
        endereco_posto = text[1]
        bandeira = text[2]

        (
            preco_comum,
            preco_aditivada,
            preco_premium,
            preco_diesel,
            preco_etanol,
            preco_gnv,
        ) = list(map(lambda x: number_or_none(x, float), text[3:]))

        print(
            [
                id_posto,
                preco_comum,
                preco_aditivada,
                preco_premium,
                preco_diesel,
                preco_etanol,
                preco_gnv,
            ]
        )
    except:
        pass
