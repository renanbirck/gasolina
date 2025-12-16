#!/usr/bin/env python3
import csv
import sqlite3

# Este script carrega dados manualmente na pesquisa mais recente,
# presumindo que ela já tenha sido criada.

CSV_SOURCE = "../parser/result.csv"
DATABASE_PATH = "../data/pesquisas.db"

connection = sqlite3.connect(DATABASE_PATH)
cursor = connection.cursor()

cursor.execute("SELECT IdPesquisa FROM Pesquisas ORDER BY IdPesquisa DESC LIMIT 1")
id_pesquisa = cursor.fetchone()[0]
processed_rows = []

print(f"O ID da pesquisa mais atual é {id_pesquisa}.")

with open(CSV_SOURCE, "r") as csvfile:
    data = csv.reader(csvfile)

    for row in data:  # Converter os tipos de dados e encaixar no formato da query.
        new_row = [id_pesquisa]

        new_row.append(int(row[0]))
        for entry in map(lambda x: float(x) if x else None, row[1:]):
            new_row.append(entry)

        processed_rows.append(new_row)
    for row in processed_rows:
        print(row)

# OK, então fazer a inserção no BD!
#
#
cursor.executemany(
    "INSERT INTO Precos(IdPesquisa, \
    IdPosto, \
    PrecoGasolinaComum, \
    PrecoGasolinaAditivada, \
    PrecoEtanol, \
    PrecoDiesel, \
    PrecoGNV, \
    PrecoGasolinaPremium) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
    processed_rows,
)
connection.commit()
