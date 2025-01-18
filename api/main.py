from fastapi import Depends, FastAPI, Request, APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from . import crud, models # não estamos usando schemas ainda
from .database import SessionLocal, engine

from fastapi.middleware.cors import CORSMiddleware

from fastapi.templating import Jinja2Templates

import uvicorn

# O arquivo principal da API.

# Carregar os modelos
models.Base.metadata.create_all(bind=engine)
app = FastAPI() 

router = APIRouter()

app.include_router(router)

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

templates = Jinja2Templates(directory="templates")

@app.get("/ultima_pesquisa", name="ultima_pesquisa")
async def ultima_pesquisa(db: Session = Depends(get_db)):
    return crud.get_ultima_pesquisa(db)

@app.get("/distribuidoras")
async def lista_distribuidoras(db: Session = Depends(get_db)):
    return crud.get_distribuidoras(db)

@app.get("/pesquisas")
async def lista_pesquisas(db: Session = Depends(get_db)):
    return crud.get_pesquisas(db)

@app.get("/postos", name="postos")
async def lista_todos_postos(db: Session = Depends(get_db)):
    return crud.get_postos(db)

@app.get("/pesquisa/{id_pesquisa}")
async def dados_pesquisa(id_pesquisa, db: Session = Depends(get_db)):
    return crud.dados_pesquisa(db, id_pesquisa) 

@app.get("/posto/{id_posto}", name="posto")
async def lista_infos_posto(id_posto, db: Session = Depends(get_db)):
    return crud.get_dados_posto(db, id_posto)


## A raiz da aplicação, mostrando a lista de todos os postos:
@app.get("/", response_class=HTMLResponse)
async def raiz_app(request: Request, db: Session = Depends(get_db)):

    postos = await lista_todos_postos(db)
    data_ultima_pesquisa = await ultima_pesquisa(db)

    dados_ultima_pesquisa = await dados_pesquisa(data_ultima_pesquisa.id, db)
    print(dados_ultima_pesquisa)

    return templates.TemplateResponse(
        request=request, name="index.html", context={"postos": postos, "ultima_pesquisa": data_ultima_pesquisa, "dados_ultima_pesquisa": dados_ultima_pesquisa} 
    )

for route in app.router.routes:
    print(route.name, route.path)

# https://stackoverflow.com/questions/75040507/how-to-access-fastapi-backend-from-a-different-machine-ip-on-the-same-local-netw
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
