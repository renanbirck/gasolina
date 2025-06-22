from sqlalchemy.orm import Session
from . import models # não estamos usando schemas ainda

from datetime import datetime

# Arquivo com a lógica CRUD  a partir da API
# no momento é só leitura, futuramente o scraper vai atualizar pela API

### Leitura
def get_ultima_pesquisa(db: Session):
    return db.query(models.Pesquisa).order_by(models.Pesquisa.id.desc()).first()

def get_pesquisas(db: Session):
    return db.query(models.Pesquisa).order_by(models.Pesquisa.id.desc()).all()

def get_distribuidoras(db: Session):
    return db.query(models.Distribuidora).all()

def get_precos_ultima_pesquisa(db: Session):
    ultima_pesquisa = get_ultima_pesquisa(db)
    return dados_pesquisa(db, ultima_pesquisa)

def get_postos(db: Session):
    query = db.query(models.PostoGasolina.id,
                 models.Distribuidora.nome,
                 models.PostoGasolina.nome,
                 models.PostoGasolina.endereco,
                 models.PostoGasolina.bairro).join(models.Distribuidora,
                                                   models.PostoGasolina.distribuidora == models.Distribuidora.id)

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
    query = db.query(models.PostoGasolina.nome,
                     models.PostoGasolina.endereco,
                     models.PostoGasolina.bairro).filter(models.PostoGasolina.id == id_posto)

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

def historico_posto(db: Session, id_posto: int):
    # Fornecendo o ID do posto ,retorna um histórico de preços dele.
    # SELECT P.DataPesquisa, IdPosto, PrecoGasolinaComum, PrecoGasolinaAditivada,
    # PrecoEtanol, PrecoDiesel, PrecoGNV FROM Precos
    # JOIN Pesquisas P ON P.IdPesquisa = Precos.IdPesquisa
    # WHERE IdPosto = id_posto
    # ORDER BY DataPesquisa

    query = db.query(models.Pesquisa.data, \
                     models.Precos.precoGasolinaComum, \
                     models.Precos.precoGasolinaAditivada, \
                     models.Precos.precoGasolinaPremium,
                     models.Precos.precoEtanol, \
                     models.Precos.precoDiesel, \
                     models.Precos.precoGNV).join(models.Pesquisa, 
                                                  models.Precos.pesquisa == models.Pesquisa.id).filter(models.Precos.posto == id_posto).order_by(models.Pesquisa.data)

    result = query.all()
    dados_historicos = [
        { "data": datetime.strptime(row[0], "%Y%m%d").strftime("%d/%m/%Y"),
          "gasolina_comum": row[1],
          "gasolina_aditivada": row[2],
          "gasolina_premium": row[3],
          "etanol": row[4],
          "diesel": row[5],
          "gnv": row[6]
        } for row in result 
    ]

    return dados_historicos

def dados_pesquisa(db: Session, id_pesquisa: int):
    # Fornecido o ID da pesquisa, retorna todos os postos que participaram dela, com os preços.

    # EM SQL puro:
    # SELECT DataPesquisa, IdPosto, NomePosto, PrecoGasolinaComum, PrecoGasolinaAditivada,
    # PrecoEtanol, PrecoDiesel, PrecoGNV FROM Precos P
    # JOIN Pesquisas Pe ON P.IdPesquisa = Pe.IdPesquisa
    # JOIN PostosGasolina PG on P.IdPosto = PG.IdPosto
    # WHERE P.IdPesquisa = {id_pesquisa}

    query = db.query(models.Pesquisa.data, 
                     models.PostoGasolina.id,
                     models.PostoGasolina.nome, 
                     models.PostoGasolina.endereco, 
                     models.PostoGasolina.bairro, 
                     models.Precos.precoGasolinaComum, 
                     models.Precos.precoGasolinaAditivada,
                     models.Precos.precoGasolinaPremium,
                     models.Precos.precoEtanol,
                     models.Precos.precoDiesel,
                     models.Precos.precoGNV) \
    .join(models.Pesquisa, models.Precos.pesquisa==models.Pesquisa.id) \
    .join(models.PostoGasolina, models.Precos.posto == models.PostoGasolina.id)  \
    .filter(models.Precos.pesquisa == id_pesquisa)
    
    result = query.all()

    postos = [
        {
            "data": datetime.strptime(row[0], "%Y%m%d").strftime("%d/%m/%Y"),
            "id": str(row[1]),
            "nome": row[2],
            "endereco": row[3],
            "bairro": row[4],
            "gasolina_comum": row[5],
            "gasolina_aditivada": row[6],
            "gasolina_premium": row[7],
            "etanol": row[8],
            "diesel": row[9],
            "GNV": row[10]
        }
        for row in result
    ]

    return postos

### Escrita

def adiciona_nova_pesquisa(db: Session, data_pesquisa: str):
    """ Cria uma linha na tabela Pesquisas para uma nova pesquisa,
        retornando um objeto com ID e data da pesquisa adicionada. """

    pesquisa = models.Pesquisa(data = data_pesquisa)

    db.add(pesquisa)
    db.commit()
    db.refresh(pesquisa)
    return pesquisa


### FIM.
