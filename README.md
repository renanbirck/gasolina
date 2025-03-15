# gasolina: raspagem e processamento dos preços dos combustíveis disponibilizados pelo PROCON de Joinville/SC

## Introdução

O PROCON de Joinville/SC, disponibiliza, por meio do seu _site_, [o preço dos combustíveis em todos os postos de gasolina do município](https://www.joinville.sc.gov.br/publicacoes/pesquisas-de-precos-combustiveis-2024/).

Assim, o objetivo deste projeto é coletar esses dados e alimentar um banco de dados, a partir do qual é gerado um _dashboard_ e tabelas nas quais é possível fazer a filtragem por bairro.

O _back-end_ do projeto é estruturado em:

* **scraper**: faz a raspagem do site do PROCON e determina o arquivo PDF a ser baixado.
* **parser**: processa o arquivo PDF, carregando os valores dele no banco de dados.
* **api**: uma API utilizando o fastapi

## Requisitos

* Para o *scraper*:
	* Python 3.11 ou mais recente;
	* requests;
	* BeautifulSoup.
* Para o parser:
	* [pymupdf](https://github.com/pymupdf/PyMuPDF/issues/) (foi o que funcionou melhor **para este layout de PDF** nos meus testes);
* Para a API:
	* FastAPI
* Para o front-end:
    * não há nenhuma dependência em específico
* TODO: ver o uso de um ORM, substituindo o uso de SQL puro.

## Execução

* Para rodar o _scraper_ dentro de um _container_:
	* Construir o _container_ - usei o podman, mas é igual para o Docker - a partir da raiz:
		`podman build -t docker-scraper -f scraper/Dockerfile .`
	* Como o _scraper_ escreve para um diretório, é preciso executar o _container_ indicando onde gravar os dados.
		`podman run -d -v [local onde gravar os dados]:/app/data docker-scraper:latest`
        É ideal que o local seja um caminho absoluto, para evitar ambiguidades.

* Para rodar o _parser_:
	* No diretório `parser`, rodar o _script_ `run_parser.sh`, fornecendo um arquivo adequado como parâmetro.

* Para rodar a _api_ durante o desenvolvimento:
    * No diretório `api`, rodar `fastapi dev main.py` para o modo de desenvolvedor.

## Deploy 

Primeiramente, é preciso construir o _container_: `podman build -t gasolina-api -f api/Dockerfile .`.

Para facilitar o _deploy_, adicionei a máquina remota no `podman system connection add REMOTE [ENDEREÇO DA MÁQUINA]:22/usr/lib/systemd/user/podman.socket` e, então, basta executar o comando `podman image scp gasolina-api:latest REMOTE::`. É preciso que o acesso via `ssh` a essa máquina remota esteja sendo feito por chave e não por senha.

Em seguida, na máquina remota, é preciso executar o comando `podman run -dt -v [LOCAL ONDE FICA O BD]:/data:Z --name gasolina-api -p 8000:8000 --replace gasolina-api` para subir o servidor. O local onde fica o BD deve ser configurado conforme o servidor.  

No servidor já deverá existir um proxy reverso, como o Apache ou o nginx, operacional. Ele irá receber as requisições na porta 80 e encaminhar para a porta 8000. 

Um mínimo exemplo de configuração do _nginx_ é:

    server {

            server_name [URL DA APLICAÇÃO];

            listen 80;
            listen [::]:80;

            location / {
                    proxy_pass http://localhost:8000;
                    include uwsgi_params;
            }

    }

sendo preciso, também, gerar um certificado (se estivermos usando o _Let's Encrypt_, por exemplo) e configurar o nginx corretamente. Não vou entrar em detalhes aqui, porque cada configuração do _nginx_ será diferente.

## Coisas a fazer:

(em nenhuma ordem)
### Scraper e parser:
* A estrutura dos PDFs mudou conforme o tempo, então preciso ver como fazer. Provavelmente vou fazer _data wrangling_ na mão e fornecer um CSV.
* Verificar se vale a pena fazer a raspagem de forma assíncrona/paralela (acredito que não).
 Automatizar o _deploy_.
* Fazer a raspagem comunicar via API em vez de chamadas SQL diretamente no BD.

### API:
* Atualmente, a imagem está muito grande. Ver se eu consigo reduzir o tamanho dela.
* Integrar os testes com o _container_.
* Configurar Actions para rodar os testes e fazer o _deploy_ automaticamente.

### Front-end: 
* Integração com o Google Maps ou OpenStreetMap. 
* Usar TypeScript e algum framework, como React ou vue, no front-end.

## Problemas encontrados

* A tabela fornecida pela prefeitura é inconsistente, com postos repetidos ou que mudaram de nome. Isso irá influenciar na estrutura do BD. 

## Licença

Licenciado sob a licença MIT; ver o arquivo LICENSE para mais detalhes.
