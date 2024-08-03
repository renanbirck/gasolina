#!/usr/bin/env python3

# data-explorer.py: um front-end simples para consulta aos dados da pesquisa.
# Criado para aprender o uso do streamlit.

CAMINHO_DB = '../parser/pesquisas.db'  # Onde está o BD com os dados das pesquisas?
                                       # Idealmente, isso seria definido por uma variável de ambiente.

import sqlite3, pandas as pd, streamlit as st

st.write("Hello, World")

conexao_DB = sqlite3.connect(CAMINHO_DB)

# Teste da conexão: verificar se conseguimos acessar as pesquisas

datas_pesquisas = pd.read_sql_query("SELECT * FROM Pesquisas", conexao_DB)

st.write("Pesquisas disponíveis no BD:")
st.write(datas_pesquisas)