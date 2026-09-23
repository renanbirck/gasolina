from fastapi import Depends, FastAPI, Request, HTTPException, Header
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from . import crud, models # não estamos usando schemas ainda
from .database import SessionLocal, engine, aplica_migracoes

from os import environ  # para decidir se estamos em BD de teste ou de produção
from pathlib import Path
from typing import Optional
import uvicorn, logging, secrets

# Os diretórios são relativos a este arquivo, e não ao diretório de onde a API foi iniciada.
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"

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
try:
    aplica_migracoes()
except IntegrityError as e:
    # Só acontece se já houver preços duplicados no BD; não impede a API de subir.
    logging.error(f'Não foi possível criar os índices do BD (há dados duplicados?): {e}')

app = FastAPI(exception_handlers=exception_handlers)

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

templates = Jinja2Templates(directory=TEMPLATES_DIR)

# As rotas de escrita exigem o cabeçalho X-API-Key igual à variável de ambiente
# GASOLINA_API_KEY. Se ela não estiver setada, a escrita fica desativada.
def verifica_chave_api(x_api_key: Optional[str] = Header(default=None)):
    chave = environ.get("GASOLINA_API_KEY")
    if not chave:
        raise HTTPException(status_code=403, detail="Escrita desativada: GASOLINA_API_KEY não está setada.")
    if not x_api_key or not secrets.compare_digest(x_api_key, chave):
        raise HTTPException(status_code=401, detail="Chave da API inválida.")

def erro_integridade(db: Session, e: IntegrityError, msg_duplicado: str):
    """ Desfaz a transação e monta a resposta de erro para um IntegrityError. """
    db.rollback()
    if "UNIQUE constraint failed" in str(e):
        msg = msg_duplicado
    else:
        msg = f"Violação de integridade no BD: {e.orig}"
    logging.error(msg)
    return JSONResponse(status_code=422,
                        content=jsonable_encoder({"code": 422, "msg": msg}))

# As rotas de leitura são 'async def': as consultas no SQLite levam poucos milissegundos, e
# rodar no próprio event loop é mais rápido do que passar por uma thread. Isso só é seguro
# porque o BD usa NullPool e WAL (ver database.py): não há pool para esgotar, e uma leitura
# nunca espera por uma escrita. As rotas de escrita são 'def' e rodam em threads, porque
# podem ter que esperar pelo lock do SQLite.

@app.get("/environment")
async def ambiente():
    if "DB_PATH" in environ:
        logging.info(f'DB_PATH: {environ["DB_PATH"]}... estamos no ambiente de desenvolvimento')
        environment = "DEV"
    else:
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
async def dados_pesquisa(id_pesquisa: int, db: Session = Depends(get_db)):
    return crud.dados_pesquisa(db, id_pesquisa)

@app.get("/posto/{id_posto}", name="posto")
async def lista_infos_posto(id_posto: int, db: Session = Depends(get_db)):
    return crud.get_dados_posto(db, id_posto)

# O ':int' faz com que um ID não numérico nem case com a rota, caindo no 404.
@app.get("/historico/{id_posto:int}", name="historico_posto", response_class=HTMLResponse)
async def historico_posto(id_posto: int, request: Request, db: Session = Depends(get_db)):
    dados_posto = crud.get_dados_posto(db, id_posto)
    if not dados_posto:  # O posto não existe
        return templates.TemplateResponse(request=request,
                                          name="404.html",
                                          status_code=404)

    dados_historico_posto = crud.historico_posto(db, id_posto)

    return templates.TemplateResponse(
           request=request, name="info_posto.html",
           context={"dados_posto": dados_posto[0],
                    "dados_historico_posto": dados_historico_posto}
           )

@app.post("/pesquisa/nova", dependencies=[Depends(verifica_chave_api)])
def cria_nova_pesquisa(pesquisa: models.PesquisaModel,
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
        return erro_integridade(db, e, f"Já há uma pesquisa para essa data: {pesquisa.data}.") # pyright: ignore[reportReturnType]

@app.post("/distribuidora/nova", dependencies=[Depends(verifica_chave_api)])
def cria_nova_distribuidora(distribuidora: models.DistribuidoraModel,
                            db: Session = Depends(get_db)) -> models.DistribuidoraModel:
    logging.info(f'Criando nova distribuidora: {distribuidora.nome}.')

    try:
        nova_distribuidora = crud.adiciona_nova_distribuidora(db, distribuidora.nome)
        logging.info(f'O ID da distribuidora nova é {nova_distribuidora.id}.')
        return nova_distribuidora
    except IntegrityError as e:
        logging.error(f'Erro ao adicionar distribuidora nova!')
        return erro_integridade(db, e, f"Já existe a distribuidora: {distribuidora.nome}.") # pyright: ignore[reportReturnType]

@app.post("/posto/novo", dependencies=[Depends(verifica_chave_api)])
def cria_novo_posto(posto: models.PostoModel,
                    db: Session = Depends(get_db)) -> models.PostoModel: # pyright: ignore[reportReturnType]
    try:
        logging.info(f'Criando novo posto {posto}.')
        novo_posto = crud.adiciona_novo_posto(db, posto) # pyright: ignore[reportArgumentType]
        logging.info(f'O ID do posto novo é {novo_posto.id}.')
        return novo_posto
    except IntegrityError as e:
        logging.warning('Erro ao adicionar posto novo!')
        return erro_integridade(db, e, f"Já existe o posto com o ID {posto.id}.") # pyright: ignore[reportReturnType]
    except ValueError as v:
        return JSONResponse(status_code=422,
                            content=jsonable_encoder({
                                "code": 422,
                                "msg": str(v)})
                            ) # pyright: ignore[reportReturnType]
    
    
@app.post("/preco/novo", dependencies=[Depends(verifica_chave_api)])
def cria_novo_preco(preco: models.PrecoModel,
                    db: Session = Depends(get_db)) -> models.PrecoModel:
    
    logging.info(f'Criando novo preço {preco}.')

    try:
        novo_preco = crud.adiciona_novo_preco(db, preco)
        logging.info(f'O ID do preço novo é {novo_preco.id}.')
        return novo_preco
    except IntegrityError as e:
        logging.error('Erro ao adicionar preço novo!')
        return erro_integridade(db, e, f"Já existe o preço para o posto {preco.posto} na pesquisa {preco.pesquisa}.") # pyright: ignore[reportReturnType]
    except ValueError as v:
        return JSONResponse(status_code=422,
                            content=jsonable_encoder({
                                "code": 422,
                                "msg": str(v)})
                            ) # pyright: ignore[reportReturnType]

####### Configurações
## Para exibir imagens a partir do diretório templates/images.
app.mount("/images", StaticFiles(directory=TEMPLATES_DIR / "images"), name='images')

## Para termos um diretório com as bibliotecas.
app.mount("/libs", StaticFiles(directory=TEMPLATES_DIR / "libs"), name='libs')
app.mount("/style", StaticFiles(directory=TEMPLATES_DIR / "style"), name='style')

#######
## A raiz da aplicação, mostrando a lista de todos os postos:
@app.get("/", response_class=HTMLResponse)
async def raiz_app(request: Request, db: Session = Depends(get_db)):

    data_ultima_pesquisa = crud.get_ultima_pesquisa(db)
    # O BD pode estar vazio (ambiente novo ou de testes).
    dados_ultima_pesquisa = crud.dados_pesquisa(db, data_ultima_pesquisa.id) if data_ultima_pesquisa else []

    return templates.TemplateResponse(
        request=request, name="index.html",
        context={"ultima_pesquisa": data_ultima_pesquisa,
                 "dados_ultima_pesquisa": dados_ultima_pesquisa}
    )

logging.info("--- Rotas da aplicação ---")
for route in app.router.routes:
    logging.info(f"{getattr(route, 'name', '')} {getattr(route, 'path', '')}")
logging.info("--------------------------")


# https://stackoverflow.com/questions/75040507/how-to-access-fastapi-backend-from-a-different-machine-ip-on-the-same-local-netw
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)

# FIM.
