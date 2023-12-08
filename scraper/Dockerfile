# Imagem base
FROM python:3.11

# Estabelecer um diretório onde rodar a aplicação
RUN mkdir -p /app
WORKDIR /app 
RUN cd /app 

# Copiar nossos arquivos 
COPY scraper/*.py  .    
COPY ../requirements.txt . 

# Configurar o ambiente
RUN pip install -r requirements.txt 
RUN pip install --upgrade pip 

# Para debugging, pode tirar se quiser
RUN ls -la 

# Rodar a aplicação. A aplicação escreve no diretório 'data',
# então na hora de rodar o container precisa informar
# podman run -d -v [ONDE ARMAZENAR OS DADOS NO HOST]:/app/data docker-scraper:latest
CMD ["python", "scraper.py"]