# Imagem base
FROM python:3.11

# Copiar nossos arquivos 
COPY *.py  .    
COPY ../requirements.txt . 

# Configurar o ambiente
RUN pip install -r requirements.txt 
RUN pip install --upgrade pip 

# Rodar a aplicação
CMD ["python", "./scraper.py"]