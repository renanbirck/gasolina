from sqlalchemy.orm import Session
from . import models # não estamos usando schemas ainda

# Arquivo com a lógica CRUD (na verdade, só R mesmo, porque a gente não faz atualização)
# a partir da API - talvez no futuro eu faça isso, fazendo o scraper conversar
# via API.

def get_pesquisas(db: Session):
    return db.query(models.Pesquisa).all()

def get_distribuidoras(db: Session):
    return db.query(models.Distribuidora).all()