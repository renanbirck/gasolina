console.log("Olá mundo!")

// Carregar os dados da API
const requestPesquisas = new Request("http://127.0.0.1:8000/pesquisas")

fetch(requestPesquisas) // Pega os dados...
.then(retorno => retorno.json())
.then(dadosPesquisas => {
  console.log(dadosPesquisas)

  dadosPesquisas.forEach((element) => {
    option = document.createElement("option");
    option.value = element.id;
    option.text = element.data;
    document.querySelector("#listaMeses").add(option);
  })
})
.catch(rejected => { // Deu errado
    console.log("Erro ao puxar os dados da API! " + rejected);
});