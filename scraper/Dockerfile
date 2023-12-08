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

RUN ls -la 

# Rodar a aplicação
CMD ["python", "scraper.py"]