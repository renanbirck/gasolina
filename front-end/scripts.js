console.log("Olá mundo!")

const requestPesquisas = new Request("https://127.0.0.1:8000")

fetch(requestPesquisas)
.then(retorno => retorno.json())
.then(dadosPesquisas => {
  // do something with data
})
.catch(rejected => {
    console.log("Erro ao puxar os dados da API! " + rejected);
});