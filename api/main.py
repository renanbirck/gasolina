from fastapi import Depends, FastAPI, Request, APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from . import crud, models # não estamos usando schemas ainda
from .database import SessionLocal, engine

from fastapi.middleware.cors import CORSMiddleware

from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn

# Tratadores de exceções para erro 404 e 500

async def not_found_error(request: Request, exception: HTTPException):
     return templates.TemplateResponse(
            request=request, name="404.html", 
            status_code=404)

async def internal_error(request: Request, exception: HTTPException):
     return templates.TemplateResponse(
            request=request, name="500.html", 
            status_code=500)

exception_handlers = {
    404: not_found_error,
    500: internal_error
}

# O arquivo principal da API.

# Carregar os modelos
models.Base.metadata.create_all(bind=engine)
app = FastAPI(exception_handlers=exception_handlers) 

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

@app.get("/historico/{id_posto}", name="historico_posto", response_class=HTMLResponse)
async def historico_posto(id_posto, request: Request, db: Session = Depends(get_db)):
   
    try:
       dados_posto = await lista_infos_posto(int(id_posto), db)
       print(dados_posto)

       dados_historico_posto = crud.historico_posto(db, int(id_posto))
       print(dados_historico_posto)

       return templates.TemplateResponse(
                request=request, name="info_posto.html", 
                context={"dados_posto": dados_posto[0],
                         "dados_historico_posto": dados_historico_posto}
                )
    except:  # O posto não existe
      return templates.TemplateResponse(
            request=request, name="404.html", 
            status_code=404)

       


## Para exibir imagens 
app.mount("/images", StaticFiles(directory="templates/images"), name='images')

## Para termos um diretório com as bibliotecas
app.mount("/libs", StaticFiles(directory="templates/libs"), name='libs')
app.mount("/style", StaticFiles(directory="templates/style"), name='style')

## A raiz da aplicação, mostrando a lista de todos os postos:
@app.get("/", response_class=HTMLResponse)
async def raiz_app(request: Request, db: Session = Depends(get_db)):

    data_ultima_pesquisa = await ultima_pesquisa(db)
    dados_ultima_pesquisa = await dados_pesquisa(data_ultima_pesquisa.id, db)

    print(data_ultima_pesquisa)
    return templates.TemplateResponse(
        request=request, name="index.html", context={"ultima_pesquisa": data_ultima_pesquisa, "dados_ultima_pesquisa": dados_ultima_pesquisa} 
    )

print("--- Rotas da aplicação ---")
for route in app.router.routes:
    print(route.name, route.path)
print("--------------------------")


# https://stackoverflow.com/questions/75040507/how-to-access-fastapi-backend-from-a-different-machine-ip-on-the-same-local-netw
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
