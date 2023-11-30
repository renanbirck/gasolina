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
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS Distribuidoras(\
                             IdDistribuidora INT PRIMARY KEY,\
                             NomeDistribuidora VARCHAR(24) UNIQUE NOT NULL\
                            );")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS PostosGasolina(\
                                IdPosto INT PRIMARY KEY,\
                                IdDistribuidora INT NOT NULL,\
                                NomePosto VARCHAR(255) NOT NULL,\
                                EnderecoPosto VARCHAR(255) NOT NULL,\
                                BairroPosto VARCHAR(32) NOT NULL,\
                                FOREIGN KEY (IdDistribuidora)\
                                    REFERENCES Distribuidoras(IdDistribuidora)\
                                    ON DELETE RESTRICT\
                             );")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS Pesquisas(\
                                IdPesquisa INT PRIMARY KEY,\
                                DataPesquisa VARCHAR(24) NOT NULL);")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS Precos(\
                                IdPreco INT PRIMARY KEY,\
                                IdPesquisa INT,\
                                IdPosto INT,\
                                PrecoGasolinaComum INTEGER,\
                                PrecoGasolinaAditivada INTEGER,\
                                PrecoEtanol INTEGER,\
                                PrecoDiesel INTEGER,\
                                FOREIGN KEY (IdPesquisa)\
                                    REFERENCES Pesquisas(IdPesquisa)\
                                    ON DELETE RESTRICT,\
                                FOREIGN KEY (IdPosto)\
                                    REFERENCES Posto(IdPosto)\
                                    ON DELETE RESTRICT);")


        self.connection.commit()

    
