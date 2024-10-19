from sqlalchemy.orm import Session
from . import models # não estamos usando schemas ainda

# Arquivo com a lógica CRUD  a partir da API
# no momento é só leitura, futuramente o scraper
# vai atualizar pela API

def get_pesquisas(db: Session):
    return db.query(models.Pesquisa).all()

def get_distribuidoras(db: Session):
    return db.query(models.Distribuidora).all()

def get_postos(db: Session):
    query = db.query(models.PostoGasolina.id, 
                 models.Distribuidora.nome,
                 models.PostoGasolina.nome, 
                 models.PostoGasolina.endereco, 
                 models.PostoGasolina.bairro).join(models.Distribuidora, models.PostoGasolina.distribuidora == models.Distribuidora.id)
    
    result = query.all()
    
    # XXX: pedi ajuda para o ChatGPT aqui, ver se tem como fazer de forma mais elegante

    # Convert the list of tuples to a list of dictionaries
    postos = [
        {
            "id": row[0],
            "distribuidora_nome": row[1],
            "posto_nome": row[2],
            "endereco": row[3],
            "bairro": row[4]
        }
        for row in result
    ]
    
    return postos