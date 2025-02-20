FROM python:3.13-alpine

# Estabelecer um local para rodar a aplicação
RUN mkdir -p /app /app/templates /app/templates/images

# Onde fica o BD
RUN mkdir -p /data   
WORKDIR /app 
RUN cd /app 

EXPOSE 8000 

# Copiar os arquivos da aplicação
COPY api/*.py .
COPY ../requirements.txt . 
COPY api/templates/ templates
#COPY api/templates/images/* templates/images

# Configurar o ambiente
RUN pip install --upgrade pip 
RUN pip install fastapi sqlalchemy fastapi[standard]

# Rodar a aplicação.  A aplicação lê do diretório 'data', então precisa informar
# podman run -d -v [RAIZ DA APLICAÇÃO]/data:/data:Z gasolina-api:latest -p 8000:8000 
#
# (o :Z é por causa do SELinux, TODO: ver como resolver problema com ele)

RUN ls -la 
RUN pwd

# Rodar em produção, escutando no http://0.0.0.0
CMD ["fastapi", "run"]
