# gasolina: raspagem e processamento dos preços dos combustíveis disponibilizados pelo PROCON de Joinville/SC

## Introdução

O PROCON de Joinville/SC, disponibiliza, por meio do seu _site_, [o preço dos combustíveis em todos os postos de gasolina do município](https://www.joinville.sc.gov.br/publicacoes/pesquisas-de-precos-combustiveis-2023/).

Assim, o objetivo deste projeto é coletar esses dados e alimentar um banco de dados, a partir do qual é gerado um _dashboard_ e tabelas nas quais é possível fazer a filtragem por bairro.

O _back-end_ do projeto é estruturado em três módulos:

* **scraper**: faz a raspagem do site do PROCON e determina o arquivo PDF a ser baixado.
* **processor**: processa o arquivo PDF, carregando os valores dele no banco de dados.
* **api**: disponibiliza os dados coletados para o _front-end_.

## Requisitos

* Para o *scraper*:
	* Python 3.11 ou mais recente;
	* requests;
	* BeautifulSoup.
* Para o *processor*:
	* [pypdfium2](https://github.com/pypdfium2-team/pypdfium2) (foi o que funcionou melhor **para este layout de PDF** nos meus testes);
* TODO: definir como será feita a API
* TODO: definir como será feito o front-end

## Execução

* TODO: escrever Dockerfiles
* TODO: configurar Actions para rodar os testes automaticamente
* TODO: automatizar o _deploy_ 
  
## Licença

Licenciado sob a licença MIT; ver o arquivo LICENSE para mais detalhes.
