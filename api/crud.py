from sqlalchemy.orm import Session
from . import models # não estamos usando schemas ainda

# Arquivo com a lógica CRUD  a partir da API
# no momento é só leitura, futuramente o scraper
# vai atualizar pela API

def get_ultima_pesquisa(db: Session):
    return db.query(models.Pesquisa).order_by(models.Pesquisa.id.desc()).first()

def get_pesquisas(db: Session):
    return db.query(models.Pesquisa).order_by(models.Pesquisa.id.desc()).all()

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
    # O que o FastAPI precisa é de uma lista de dicionários, e a query retornou
    # uma lista de tuplas. 
    
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

def get_dados_posto(db: Session, id_posto: int):
    query = db.query(models.PostoGasolina.nome, models.PostoGasolina.endereco, models.PostoGasolina.bairro).filter(models.PostoGasolina.id == id_posto)
    result = query.all() 

    dados_posto = [
        {
            "id": id_posto,
            "nome": row[0],
            "endereco": row[1],
            "bairro": row[2],
        }
        for row in result
    ]
 
    return dados_posto

def dados_pesquisa(db: Session, id_pesquisa: int):
    # Fornecido o ID da pesquisa, retorna todos os postos que participaram dela, com os preços.
    
    # EM SQL puro:
    # SELECT DataPesquisa, NomePosto, PrecoGasolinaComum, PrecoGasolinaAditivada, PrecoEtanol, PrecoDiesel, PrecoGNV FROM Precos P 
    # JOIN Pesquisas Pe ON P.IdPesquisa = Pe.IdPesquisa 
    # JOIN PostosGasolina PG on P.IdPosto = PG.IdPosto
    # WHERE P.IdPesquisa = {id_pesquisa}

    query = db.query(models.Pesquisa.data, models.PostoGasolina.nome, models.Precos.precoGasolinaComum, models.Precos.precoGasolinaAditivada,
                     models.Precos.precoEtanol,models.Precos.precoDiesel,models.Precos.precoGNV) \
    .join(models.Pesquisa, models.Precos.pesquisa==models.Pesquisa.id) \
    .join(models.PostoGasolina, models.Precos.posto == models.PostoGasolina.id)  \
    .filter(models.Precos.pesquisa == id_pesquisa)
    

    result = query.all()

    print(result)
    dados_pesquisa = [
        {
            "id": row[0],
            "nome": row[1],
            "gasolina_comum": row[2],
            "gasolina_aditivada": row[3],
            "etanol": row[4],
            "diesel": row[5],
            "GNV": row[6]
        }
        for row in result
    ]

    return dados_pesquisa
