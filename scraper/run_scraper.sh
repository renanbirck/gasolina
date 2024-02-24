#!/usr/bin/env bash

run_scraper () {
	echo "Chamando o scraper para o ano de $1."
	./scraper.py "$1"
}

if [ $# -eq 0 ]
then
	echo "Forneça um ano para baixar os PDFs, ou uma sequência de anos."
	exit 1
elif [ $# -eq 1 ]
then 
	run_scraper $1
elif [ $# -eq 2 ] 
then 
	for YEAR in $(seq $1 $2)
	do
		run_scraper $YEAR
	done
fi

