#!/usr/bin/env python3

# Este módulo trata das operações com o banco de dados.

import sqlite3, logging

class Database:
    connection, cursor = None, None
    file_name = None

    def __init__(self, file_name='pesquisas.db'):
        self.file_name = file_name
        self.initialize_DB()

    def __del__(self):
        self.connection.commit()

    def initialize_DB(self):
        logging.info(f"Criando o BD com o nome {self.file_name}.")
        self.connection = sqlite3.connect(self.file_name)
        self.cursor = self.connection.cursor()
