from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Numeric
from sqlalchemy.orm import relationship
from .database import Base # Os modelos herdam de Base
from pydantic import BaseModel

class PesquisaModel(BaseModel):
    id: int = None  # O ID da pesquisa é gerado automaticamente, por ser primary key
    data: str

class DistribuidoraModel(BaseModel):
    id: int = None
    nome: str

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

class Precos(Base):
    __tablename__ = "Precos"
    id = Column("IdPreco", Integer, primary_key=True)
    pesquisa = Column("IdPesquisa", Integer)
    posto = Column("IdPosto", Integer)
    precoGasolinaComum = Column("PrecoGasolinaComum", Numeric)
    precoGasolinaAditivada = Column("PrecoGasolinaAditivada", Numeric)
    precoGasolinaPremium = Column("PrecoGasolinaPremium", Numeric)
    precoEtanol = Column("PrecoEtanol", Numeric)
    precoDiesel = Column("PrecoDiesel", Numeric)
    precoGNV = Column("PrecoGNV", Numeric)
