# gasolina: raspagem e processamento dos preços dos combustíveis disponibilizados pelo PROCON de Joinville/SC

## Introdução

O PROCON de Joinville/SC, disponibiliza, por meio do seu _site_, [o preço dos combustíveis em todos os postos de gasolina do município](https://www.joinville.sc.gov.br/publicacoes/pesquisas-de-precos-combustiveis-2023/).

Assim, o objetivo deste projeto é coletar esses dados e alimentar um banco de dados, a partir do qual é gerado um _dashboard_ e tabelas nas quais é possível fazer a filtragem por bairro.

O _back-end_ do projeto é estruturado em três módulos:

* **scraper**: faz a raspagem do site do PROCON e determina o arquivo PDF a ser baixado.
* **parser**: processa o arquivo PDF, carregando os valores dele no banco de dados.
* **api**: disponibiliza os dados coletados para o _front-end_.

## Requisitos

* Para o *scraper*:
	* Python 3.11 ou mais recente;
	* requests;
	* BeautifulSoup.
* Para o parser:
	* [pymupdf](https://github.com/pymupdf/PyMuPDF/issues/) (foi o que funcionou melhor **para este layout de PDF** nos meus testes);
	* TODO: continuar a parte de processamento do PDF
* TODO: ver o uso de um ORM, substituindo o uso de SQL puro.
* TODO: definir como será feita a API.
* TODO: definir como será feito o front-end.

## Execução

* Para rodar o _scraper_:
	* Construir o _container_ - usei o podman, mas é igual para o Docker - a partir do diretório atual:
		`podman build -t docker-scraper -f scraper/Dockerfile .`
	* Como o _scraper_ escreve para um diretório, é preciso executar o _container_ indicando onde gravar os dados.
		`podman run -d -v [local onde gravar os dados]:/app/data docker-scraper:latest`

* Para rodar o _parser_:
	* No diretório `parser`, rodar o _script_ `run_parser.sh`, fornecendo um arquivo adequado como parâmetro.

* TODO: a estrutura dos PDFs mudou conforme o tempo, então preciso ver como fazer. Provavelmente vou fazer _data wrangling_ na mão e fornecer um CSV.
* TODO: integrar os testes com o _container_.
* TODO: escrever Dockerfiles para o resto
* TODO: configurar Actions para rodar os testes automaticamente
* TODO: automatizar o _deploy_ 
* TODO: ver se há alguma forma mais inteligente, evitando raspagem de PDF ou ao menos tornando ela mais resistenta a mudanças no layout do PDF.

## Licença

Licenciado sob a licença MIT; ver o arquivo LICENSE para mais detalhes.
