#!/usr/bin/env python3 
"""
    Um pequeno script para converter a coluna de datas das pesquisas
    para o formato ISO8601 (AAAA-MM-DD)
"""

import sqlite3, logging
from datetime import datetime 

DATABASE_PATH = '../data/pesquisas.db'

logging.info("Conectando ao banco de dados...")
try:
    connection = sqlite3.connect(DATABASE_PATH)
except:
    logging.fatal("Não foi possível conectar ao banco de dados!")

cursor = connection.cursor()
cursor.execute("SELECT * FROM Pesquisas ORDER BY IdPesquisa")
output = cursor.fetchall()

changes = [(datetime.strptime(original_date, "%d/%m/%Y").strftime("%Y%m%d"), id) for (id, original_date) in output]

cursor.executemany("UPDATE Pesquisas SET DataPesquisa = ? WHERE IdPesquisa = ?", changes)
connection.commit()
