FROM python:3.13

# Estabelecer um local para rodar a aplicação
RUN mkdir -p /app 

# Onde fica o BD
RUN mkdir -p /data   
WORKDIR /app 
RUN cd /app 

# Copiar os arquivos da aplicação
COPY api/*.py .
COPY ../requirements.txt . 

# Configurar o ambiente
RUN pip install --upgrade pip 
RUN pip install fastapi sqlalchemy fastapi[standard]

# Rodar a aplicação.  A aplicação lê do diretório 'data', então precisa informar
# podman run -d -v [RAIZ DA APLICAÇÃO]/data:/data:Z gasolina-api:latest
#
# (o :Z é por causa do SELinux, TODO: ver como resolver problema com ele)

RUN ls -la 
RUN pwd
CMD ["fastapi", "dev", "main.py"]