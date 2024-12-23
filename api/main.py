from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models # não estamos usando schemas ainda
from .database import SessionLocal, engine

from fastapi.middleware.cors import CORSMiddleware

import uvicorn

# O arquivo principal da API.

# Carregar os modelos
models.Base.metadata.create_all(bind=engine)
app = FastAPI() 

# Configurações de CORS para permitir o uso da API.

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

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

@app.get("/ultima_pesquisa")
async def ultima_pesquisa(db: Session = Depends(get_db)):
    return crud.get_ultima_pesquisa(db)

@app.get("/distribuidoras")
async def lista_distribuidoras(db: Session = Depends(get_db)):
    return crud.get_distribuidoras(db)

@app.get("/pesquisas")
async def lista_pesquisas(db: Session = Depends(get_db)):
    return crud.get_pesquisas(db)

@app.get("/postos")
async def lista_todos_postos(db: Session = Depends(get_db)):
    return crud.get_postos(db)

@app.get("/pesquisa/{id_pesquisa}")
async def lista_postos_da_pesquisa(id_pesquisa, db: Session = Depends(get_db)):
    return crud.dados_pesquisa(db, id_pesquisa) 

# https://stackoverflow.com/questions/75040507/how-to-access-fastapi-backend-from-a-different-machine-ip-on-the-same-local-netw
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
