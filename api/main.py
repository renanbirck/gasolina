from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models # não estamos usando schemas ainda
from .database import SessionLocal, engine

# O arquivo principal da API.

# Carregar os modelos
models.Base.metadata.create_all(bind=engine)
app = FastAPI() 

# carregar o BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    return {"message": "Hello, World!"}

@app.get("/distribuidoras")
async def lista_distribuidoras(db: Session = Depends(get_db)):
    return crud.get_distribuidoras(db)

@app.get("/pesquisas")
async def lista_pesquisas(db: Session = Depends(get_db)):
    return crud.get_pesquisas(db)

@app.get("/postos/{id_pesquisa}")
async def lista_postos_da_pesquisa(id_pesquisa):
    pass 

@app.get("/pesquisa/{id_pesquisa}")
async def pega_dados_pesquisa(id_pesquisa):
    pass