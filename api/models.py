from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Numeric, UniqueConstraint
from typing import Optional
from sqlalchemy.orm import relationship
from .database import Base # Os modelos herdam de Base
from pydantic import BaseModel

class PesquisaModel(BaseModel):
    id: int = None  # O ID da pesquisa é gerado automaticamente, por ser primary key
    data: str

class DistribuidoraModel(BaseModel):
    id: int = None
    nome: str

class PostoModel(BaseModel):
    id: int
    distribuidora: str  # O nome da distribuidora será resolvido depois, dentro do CRUD
    nome: str
    endereco: str
    bairro: str

class PrecoModel(BaseModel):    
    id: int = None
    pesquisa: int  # ID da pesquisa
    posto: int  # ID do posto

    ## Pegadinha: float não pode ser null, então usamos Optional[float] para permitir que seja None.
    precoGasolinaComum: Optional[float] = None
    precoGasolinaAditivada: Optional[float] = None 
    precoGasolinaPremium: Optional[float] = None 
    precoEtanol: Optional[float] = None 
    precoDiesel: Optional[float] = None 
    precoGNV: Optional[float] = None 

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
    distribuidora = Column("IdDistribuidora", Integer, ForeignKey('Distribuidoras.IdDistribuidora', ondelete='RESTRICT'))
    nome = Column("NomePosto", String, nullable=False)
    endereco = Column("EnderecoPosto", String, nullable=False)
    bairro = Column("BairroPosto", String, nullable=False)

class Preco(Base):
    __tablename__ = "Precos"
    id = Column("IdPreco", Integer, primary_key=True)
    pesquisa = Column("IdPesquisa", Integer)
    posto = Column("IdPosto", Integer)
    precoGasolinaComum = Column("PrecoGasolinaComum", Numeric, nullable=True)
    precoGasolinaAditivada = Column("PrecoGasolinaAditivada", Numeric, nullable=True)
    precoGasolinaPremium = Column("PrecoGasolinaPremium", Numeric, nullable=True)
    precoEtanol = Column("PrecoEtanol", Numeric, nullable=True)
    precoDiesel = Column("PrecoDiesel", Numeric, nullable=True)
    precoGNV = Column("PrecoGNV", Numeric, nullable=True)

    # Não pode haver uma pesquisa com o mesmo posto mais de uma vez.
    __table_args__ = (
        UniqueConstraint('IdPesquisa', 'IdPosto', name='uix_pesquisa_posto'),
    )

