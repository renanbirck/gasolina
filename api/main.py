from fastapi import FastAPI

app = FastAPI() 

@app.get("/")
async def root():
    return {"message": "Hello, World!"}

@app.get("/pesquisas")
async def lista_pesquisas():
    pass

@app.get("/postos/{id_pesquisa}")
async def lista_postos_da_pesquisa(id_pesquisa):
    pass 

@app.get("/pesquisa/{id_pesquisa}")
async def pega_dados_pesquisa(id_pesquisa):
    pass