FROM python:3.13-alpine

# Onde fica o BD
RUN mkdir -p /app /data
WORKDIR /app 

EXPOSE 8000 

# Instalar as dependências antes de copiar o código, para o cache do build
# só ser invalidado quando elas mudarem.
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar os arquivos da aplicação
COPY api/*.py .
COPY api/templates/ templates

# Rodar a aplicação.  A aplicação lê do diretório 'data', então precisa informar
# podman run -d -v [RAIZ DA APLICAÇÃO]/data:/data:Z gasolina-api:latest -p 8000:8000 
#
# (o :Z é por causa do SELinux, TODO: ver como resolver problema com ele)
#
# O container roda como root de propósito: no podman rootless, o root do container é
# o usuário do host, que é o dono do diretório do BD. Um usuário não-root no container
# não conseguiria gravar no BD (nem nos arquivos -wal/-shm do SQLite).

# Rodar em produção, escutando no http://0.0.0.0
CMD ["fastapi", "run"]
