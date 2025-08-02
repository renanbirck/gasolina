#!/usr/bin/env bash 
#
# Este script converte o arquivo db em um schema que pode ser importado posteriormente,
# para evitar ter arquivos binários no nosso git.

set -e 

DB_FILE='pesquisas.db'
DUMP_FILE='pesquisas.sql'

if [ -f "$DB_FILE" ]; then
  sqlite3 "$DB_FILE" .dump > "$DUMP_FILE"
  echo "Banco de dados escrito com sucesso!"
else
  echo "Banco de dados não encontrado em $DB_FILE"
fi
