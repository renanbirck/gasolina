#!/usr/bin/env python3

# Este módulo trata das operações com o banco de dados.

import sqlite3

class Database:
    connection, cursor = None, None

    def initialize_DB(self, file_name='pesquisas.db'):
        self.connection = sqlite3.connect(file_name)
        self.cursor = self.connection.cursor()
