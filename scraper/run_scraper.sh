#!/usr/bin/env bash

if [ $# -eq 0 ]
then
	echo "Forneça um ano para baixar os PDFs!"
	exit 1
fi

echo "Chamando o scraper para o ano de $@."
./scraper.py "$@"
