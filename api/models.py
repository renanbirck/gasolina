from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Numeric, UniqueConstraint
from typing import List, Optional
from sqlalchemy.orm import relationship
from .database import Base # Os modelos herdam de Base
from pydantic import BaseModel, Field

class PesquisaModel(BaseModel):
    id: Optional[int] = None  # O ID da pesquisa é gerado automaticamente, por ser primary key
    data: str = Field(pattern=r"^\d{8}$")  # AAAAMMDD, para que a ordenação por texto funcione

class DistribuidoraModel(BaseModel):
    id: Optional[int] = None
    nome: str

class PostoModel(BaseModel):
    id: int
    distribuidora: str  # O nome da distribuidora será resolvido depois, dentro do CRUD
    nome: str
    endereco: str
    bairro: Optional[str] = None  # Às vezes a prefeitura não informa o bairro

class PrecoModel(BaseModel):    
    id: Optional[int] = None
    pesquisa: int  # ID da pesquisa
    posto: int  # ID do posto

    ## Pegadinha: float não pode ser null, então usamos Optional[float] para permitir que seja None.
    precoGasolinaComum: Optional[float] = None
    precoGasolinaAditivada: Optional[float] = None 
    precoGasolinaPremium: Optional[float] = None 
    precoEtanol: Optional[float] = None 
    precoDiesel: Optional[float] = None 
    precoGNV: Optional[float] = None 

class PostoImportacaoModel(BaseModel):
    """ Um posto e seus preços, do jeito que o parser extrai do PDF. """
    id: int
    distribuidora: str
    nome: str
    endereco: str
    bairro: Optional[str] = None

    comum: Optional[float] = None
    aditivada: Optional[float] = None
    premium: Optional[float] = None
    etanol: Optional[float] = None
    diesel: Optional[float] = None
    gnv: Optional[float] = None

class ImportacaoModel(BaseModel):
    """ Uma pesquisa completa, importada de uma vez só (ver crud.importa_pesquisa). """
    data: str = Field(pattern=r"^\d{8}$")
    postos: List[PostoImportacaoModel] = Field(min_length=1)

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
    bairro = Column("BairroPosto", String, nullable=True)

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

