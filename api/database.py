from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from os import environ
import logging

## database.py: arquivo que trata da conexão ao BD com os dados das pesquisas.
## O modelo de dados, com as tabelas e relacionamentos, é descrito em model.py

logging.basicConfig(level=logging.INFO) # O nível de logging é INFO.


# Permitir que a variável de ambiente DB_PATH seja usada para definir onde o DB está salvo.
# Vai facilitar os testes posteriormente.

try:
    DB_URL = f"sqlite:///{environ["DB_PATH"]}"
except: # Se não especificar, é o default
    DB_URL = "sqlite:///../data/pesquisas.db" # Caminho para o BD

# Criar a conexão ao BD

logging.info(f"O caminho do BD é {DB_URL}.")

engine = create_engine(
    DB_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Até aqui, é quase tudo igual à documentação. 
