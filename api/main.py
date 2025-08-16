from fastapi import Depends, FastAPI, Request, APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from . import crud, models # não estamos usando schemas ainda
from .database import SessionLocal, engine

from os import environ  # para decidir se estamos em BD de teste ou de produção
import uvicorn, logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s"
)
logging.getLogger("uvicorn.access").setLevel(logging.INFO)

# Tratadores de exceções para erro 404 e 500

async def not_found_error(request: Request, exception: HTTPException):
    return templates.TemplateResponse(request=request,
                                      name="404.html",
                                      status_code=404)

async def internal_error(request: Request, exception: HTTPException):
    return templates.TemplateResponse(request=request,
                                      name="500.html",
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

@app.get("/environment")
async def ambiente():
    try:
        logging.info(f'DB_PATH: {environ["DB_PATH"]}... estamos no ambiente de desenvolvimento')
        environment = "DEV"

    except:
        logging.info("DB_PATH não está setado... estamos no ambiente de produção")
        environment = "PROD"

    return JSONResponse(status_code=200,
                        content=jsonable_encoder({
                                    "code": 200,
                                    "msg": f"{environment}"})
                                )

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

    dados_posto = await lista_infos_posto(int(id_posto), db)
    print(dados_posto)

    dados_historico_posto = crud.historico_posto(db, int(id_posto))
    print(dados_historico_posto)

    return templates.TemplateResponse(
            request=request, name="info_posto.html",
            context={"dados_posto": dados_posto[0],
                     "dados_historico_posto": dados_historico_posto}
            )

@app.post("/pesquisa/nova")
async def cria_nova_pesquisa(pesquisa: models.PesquisaModel,
                             db: Session = Depends(get_db)) -> models.PesquisaModel:
    logging.info(f'Criando nova pesquisa para o dia {pesquisa.data}.')

    ## TODO: Fazer alguma forma de validação dos dados, para impedir que valores
    ## ridículos sejam adicionados.

    try:
        nova_pesquisa = crud.adiciona_nova_pesquisa(db, pesquisa.data)
        logging.info(f'o ID da pesquisa nova é {nova_pesquisa.id}')
        return nova_pesquisa
    except IntegrityError as e:
        logging.error(f'Erro ao adicionar pesquisa nova! {str(e)}')
        if "UNIQUE constraint failed" in str(e):
            logging.error('Já existe uma pesquisa para essa data.')
            return JSONResponse(status_code=422,
                                content=jsonable_encoder({
                                    "code": 422,
                                    "msg": f"Já há uma pesquisa para essa data: {pesquisa.data}."})
                                ) # pyright: ignore[reportReturnType]

@app.post("/distribuidora/nova")
async def cria_nova_distribuidora(distribuidora: models.DistribuidoraModel,
                                  db: Session = Depends(get_db)) -> models.DistribuidoraModel:
    logging.info(f'Criando nova distribuidora: {distribuidora.nome}.')

    try:
        nova_distribuidora = crud.adiciona_nova_distribuidora(db, distribuidora.nome)
        logging.info(f'O ID da distribuidora nova é {nova_distribuidora.id}.')
        return nova_distribuidora
    except IntegrityError as e:
        logging.error(f'Erro ao adicionar distribuidora nova!')
        if "UNIQUE constraint failed" in str(e):
            logging.error('A distribuidora já existe (não há nada de errado nisso).')
            return JSONResponse(status_code=422,
                                content=jsonable_encoder({
                                    "code": 422,
                                    "msg": f"Já existe a distribuidora: {distribuidora.nome}."})
                                ) # pyright: ignore[reportReturnType]
    pass

@app.post("/posto/novo")
async def cria_novo_posto(posto: models.PostoModel,
                          db: Session = Depends(get_db)) -> models.PostoModel: # pyright: ignore[reportReturnType]
    try:
        logging.info(f'Criando novo posto {posto}.')
        novo_posto = crud.adiciona_novo_posto(db, posto) # pyright: ignore[reportArgumentType]
        logging.info(f'O ID do posto novo é {novo_posto.id}.')
        return novo_posto
    except IntegrityError as e:
        logging.warning('Erro ao adicionar posto novo!')
        if "UNIQUE constraint failed" in str(e):
            logging.info('Já existe o posto com esse ID (não há nada de errado nisso, porque o ID vem do PDF).')
            return JSONResponse(status_code=422,
                                content=jsonable_encoder({
                                    "code": 422,
                                    "msg": f"Já existe o posto com o ID {posto.id}."})
                                ) # pyright: ignore[reportReturnType]
    except ValueError as v:
        return JSONResponse(status_code=422,
                            content=jsonable_encoder({
                                "code": 422,
                                "msg": str(v)})
                            ) # pyright: ignore[reportReturnType]
    
    
@app.post("/preco/novo")
async def cria_novo_preco(preco: models.PrecoModel,
                          db: Session = Depends(get_db)) -> models.PrecoModel:
    
    logging.info(f'>>> {preco}')
    logging.info(f'Criando novo preço {preco}.')

    try:
        novo_preco = crud.adiciona_novo_preco(db, preco)
        logging.info(f'O ID do preço novo é {novo_preco.id}.')
        return novo_preco
    except IntegrityError as e:
        logging.error('Erro ao adicionar preço novo!')
        if "UNIQUE constraint failed" in str(e):
            return JSONResponse(status_code=422,
                                content=jsonable_encoder({
                                    "code": 422,
                                    "msg": f"Já existe o preço para o posto {preco.posto} na pesquisa {preco.pesquisa}."})
                                ) # pyright: ignore[reportReturnType]
    except ValueError as v:
        return JSONResponse(status_code=422,
                            content=jsonable_encoder({
                                "code": 422,
                                "msg": str(v)})
                            ) # pyright: ignore[reportReturnType]

####### Configurações
## Para exibir imagens a partir do diretório templates/images.
app.mount("/images", StaticFiles(directory="templates/images"), name='images')

## Para termos um diretório com as bibliotecas.
app.mount("/libs", StaticFiles(directory="templates/libs"), name='libs')
app.mount("/style", StaticFiles(directory="templates/style"), name='style')

#######
## A raiz da aplicação, mostrando a lista de todos os postos:
@app.get("/", response_class=HTMLResponse)
async def raiz_app(request: Request, db: Session = Depends(get_db)):

    data_ultima_pesquisa = await ultima_pesquisa(db)
    dados_ultima_pesquisa = await dados_pesquisa(data_ultima_pesquisa.id, db)

    print(data_ultima_pesquisa)
    return templates.TemplateResponse(
        request=request, name="index.html",
        context={"ultima_pesquisa": data_ultima_pesquisa,
                 "dados_ultima_pesquisa": dados_ultima_pesquisa}
    )

print("--- Rotas da aplicação ---")
for route in app.router.routes:
    print(route.name, route.path)
print("--------------------------")


# https://stackoverflow.com/questions/75040507/how-to-access-fastapi-backend-from-a-different-machine-ip-on-the-same-local-netw
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000, debug=True)

# FIM.
