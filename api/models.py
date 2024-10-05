from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from .database import Base # Os modelos herdam de Base

class Pesquisa(Base):
    __tablename__ =  "Pesquisas"
    IdPesquisa = Column(Integer, primary_key=True)
    DataPesquisa = Column(String, unique=True, index=False)

