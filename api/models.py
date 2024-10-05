from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from .database import Base # Os modelos herdam de Base

class Pesquisa(Base):
    __tablename__ =  "Pesquisas"
    id = Column("IdPesquisa", Integer, primary_key=True)
    data = Column("DataPesquisa", String, unique=True, index=False)

class Distribuidora(Base):
    __tablename__ = "Distribuidoras"
    id = Column("IdDistribuidora", Integer, primary_key=True)
    nome = Column("NomeDistribuidora", String, unique=True)