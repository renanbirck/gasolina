from sqlalchemy.orm import Session
from . import models # não estamos usando schemas ainda

from datetime import datetime

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s"
)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


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
                     models.Preco.precoGasolinaComum, \
                     models.Preco.precoGasolinaAditivada, \
                     models.Preco.precoGasolinaPremium,
                     models.Preco.precoEtanol, \
                     models.Preco.precoDiesel, \
                     models.Preco.precoGNV).join(models.Pesquisa, 
                                                  models.Preco.pesquisa == models.Pesquisa.id).filter(models.Preco.posto == id_posto).order_by(models.Pesquisa.data)

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
                     models.Preco.precoGasolinaComum, 
                     models.Preco.precoGasolinaAditivada,
                     models.Preco.precoGasolinaPremium,
                     models.Preco.precoEtanol,
                     models.Preco.precoDiesel,
                     models.Preco.precoGNV) \
    .join(models.Pesquisa, models.Preco.pesquisa==models.Pesquisa.id) \
    .join(models.PostoGasolina, models.Preco.posto == models.PostoGasolina.id)  \
    .filter(models.Preco.pesquisa == id_pesquisa)
    
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

### Funções para escrita no BD

def adiciona_nova_pesquisa(db: Session, data_pesquisa: str):
    """ Cria uma linha na tabela Pesquisas para uma nova pesquisa,
        retornando um objeto com ID e data da pesquisa adicionada. """

    pesquisa = models.Pesquisa(data = data_pesquisa)

    db.add(pesquisa)
    db.commit()
    db.refresh(pesquisa)
    return pesquisa


def adiciona_nova_distribuidora(db: Session, nome_distribuidora: str):
    distribuidora = models.Distribuidora(nome = nome_distribuidora)

    db.add(distribuidora)
    db.commit()
    db.refresh(distribuidora)
    return distribuidora

def adiciona_novo_posto(db: Session, posto: dict):
    ## Determinar o ID da distribuidora antes.

    logging.info(f"adicionando posto: {posto}")
    try:
        id_distribuidora = db.query(models.Distribuidora.id).where(models.Distribuidora.nome == posto.distribuidora).first()[0]
        logging.info(f"O ID da distribuidora {posto.distribuidora} é {id_distribuidora}.")
    except:
        raise ValueError(f"??? ID da distribuidora {posto.distribuidora} desconhecido?")

    novo_posto = models.PostoGasolina(id = posto.id,
                                      distribuidora = id_distribuidora,
                                      nome = posto.nome,
                                      endereco = posto.endereco,
                                      bairro = posto.bairro)

    db.add(novo_posto)
    db.commit()
    db.refresh(novo_posto)

    logging.info(f"Posto adicionado!")

    # Temos uma situação atípica aqui. O banco de dados espera uma int (id_distribuidora), mas o pydantic
    # espera uma string (nome da distribuidora). Então, iremos fazer na mão construindo a resposta manualmente.
    # TODO: Investigar se existe alguma forma menos manual de fazer isso.

    response_dict = {
        "id": novo_posto.id,
        "distribuidora": posto.distribuidora,  # Use the original string name
        "nome": novo_posto.nome,
        "endereco": novo_posto.endereco,
        "bairro": novo_posto.bairro
    }

    return models.PostoModel(**response_dict)

def adiciona_novo_preco(db: Session, preco: dict):
    """ Adiciona um novo preço para um posto em uma pesquisa. """

    logging.info(f"Adicionando nova pesquisa na tabela: {preco}")

    # Verifica se existe a pesquisa e o posto especificado 

    pesquisa_existe = db.query(models.Pesquisa).filter(models.Pesquisa.id == preco.pesquisa).first()
    if not pesquisa_existe:
        raise ValueError(f"Pesquisa com o ID informado {preco.pesquisa} não existe!")

    posto_existe = db.query(models.PostoGasolina).filter(models.PostoGasolina.id == preco.posto).first()
    if not posto_existe:
        raise ValueError(f"Posto com o ID informado {preco.posto} não existe!")
        
    novo_preco = models.Preco(pesquisa = preco.pesquisa,
                              posto = preco.posto,
                              precoGasolinaComum = preco.precoGasolinaComum,
                              precoGasolinaAditivada = preco.precoGasolinaAditivada,
                              precoGasolinaPremium = preco.precoGasolinaPremium,
                              precoEtanol = preco.precoEtanol,
                              precoDiesel = preco.precoDiesel,
                              precoGNV = preco.precoGNV
                              )

    db.add(novo_preco)
    db.commit()
    db.refresh(novo_preco)

    return novo_preco

### FIM.
