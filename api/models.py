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

class PostoGasolina(Base):
    __tablename__ = "PostosGasolina"
    id = Column("IdPosto", Integer, primary_key=True, unique=True)
    distribuidora = Column("IdDistribuidora", Integer)
    nome = Column("NomePosto", String)
    endereco = Column("EnderecoPosto", String)
    bairro = Column("BairroPosto", String)