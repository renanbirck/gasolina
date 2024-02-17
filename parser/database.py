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
        self.connection.close()

    def initialize_DB(self):
        logging.info(f"Criando o BD com o nome {self.file_name}.")
        self.connection = sqlite3.connect(self.file_name)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS Distribuidoras(\
                             IdDistribuidora INTEGER PRIMARY KEY NOT NULL,\
                             NomeDistribuidora VARCHAR(24) UNIQUE NOT NULL\
                            );")
    
        # Dois postos podem ter o mesmo nome, e pode ocorrer de terem o mesmo endereço
        # SE eles estiverem em lados opostos de uma estrada.
        self.cursor.execute("CREATE TABLE IF NOT EXISTS PostosGasolina(\
                                IdPosto INTEGER PRIMARY KEY NOT NULL,\
                                IdDistribuidora INTEGER NOT NULL,\
                                NomePosto VARCHAR(255) NOT NULL,\
                                EnderecoPosto VARCHAR(255) NOT NULL,\
                                BairroPosto VARCHAR(32) NOT NULL,\
                                FOREIGN KEY (IdDistribuidora)\
                                    REFERENCES Distribuidoras(IdDistribuidora)\
                                    ON DELETE RESTRICT\
                             );")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS Pesquisas(\
                                IdPesquisa INTEGER PRIMARY KEY NOT NULL,\
                                DataPesquisa VARCHAR(24) NOT NULL);")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS Precos(\
                                IdPreco INTEGER PRIMARY KEY NOT NULL,\
                                IdPesquisa INTEGER,\
                                IdPosto INTEGER,\
                                PrecoGasolinaComum INTEGER,\
                                PrecoGasolinaAditivada INTEGER,\
                                PrecoEtanol INTEGER,\
                                PrecoDiesel INTEGER,\
                                PrecoGNV INTEGER,\
                                FOREIGN KEY (IdPesquisa)\
                                    REFERENCES Pesquisas(IdPesquisa)\
                                    ON DELETE RESTRICT,\
                                FOREIGN KEY (IdPosto)\
                                    REFERENCES Posto(IdPosto)\
                                    ON DELETE RESTRICT);")
        self.connection.commit()

    
