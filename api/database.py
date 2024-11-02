from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

## database.py: arquivo que trata da conexão ao BD com os dados das pesquisas.
## O modelo de dados, com as tabelas e relacionamentos, é descrito em model.py

DB_URL = "sqlite:///../data/pesquisas.db" # Caminho para o BD

# Criar a conexão ao BD

engine = create_engine(
    DB_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Até aqui, é quase tudo igual à documentação. 
