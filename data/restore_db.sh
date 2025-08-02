#!/usr/bin/env bash 
#
# Este script converte o arquivo schema, gerado pelo dump_db.sh, em um banco de dados,
# para evitar ter arquivos binários no nosso git.

set -e 

DB_FILE='pesquisas.db'
DUMP_FILE='pesquisas.sql'

if [ -f "$DUMP_FILE" ]; then    # O dump existe...
  if [ ! -f "$DB_FILE" ]; then  # mas o DB não?
    sqlite3 "$DB_FILE" < "$DUMP_FILE"
  else
    echo "O DB já existe! Se você quer forçar a reconstrução a partir do dump, delete $DB_FILE. "
  fi 
else
  echo "O arquivo dump $DUMP_FILE não existe. Você rodou o dump_db.sh antes?"
fi
