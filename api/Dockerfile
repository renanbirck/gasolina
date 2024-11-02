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
# podman run -d -v [RAIZ DA APLICAÇÃO]:/data gasolina-api:latest

RUN ls -la 
CMD ["fastapi", "dev", "main.py"]