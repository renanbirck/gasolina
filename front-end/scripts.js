console.log("Olá mundo!")
console.log("aqui")
// Carregar os dados da API

const API_BASE = "http://127.0.0.1:8000"

const requestPesquisas = new Request(`${API_BASE}/pesquisas`)

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

// e então, quando o usuário escolher uma pesquisa, gerar a tabela
window.onload = function() { 
  document.querySelector("#listaMeses").onchange = function() {
    console.log(`Você escolheu a pesquisa ${document.querySelector("#listaMeses").value}`);
    atualizaTabelaPesquisas();
  }
}

function atualizaTabelaPesquisas() { 
  tabela = document.querySelector("#tabelaResultados")

  console.log("Atualizando a tabela...");
  pegaDadosPesquisa(document.querySelector("#listaMeses").value)
  .then(
    retorno => { 
      retorno.forEach((linhaRetornada) => {
        html = `<tr> <td> ${linhaRetornada.nome} </td> 
                     <td> ${linhaRetornada.gasolina_comum} </td> 
                     <td> ${linhaRetornada.gasolina_aditivada} </td>
                     <td> ${linhaRetornada.etanol} </td>
                     <td> ${linhaRetornada.diesel} </td>
                     <td> ${linhaRetornada.GNV} </td>
                </tr>`;
        tabela.innerHTML += html;
      })

      


    }
    
  );

}

function pegaDadosPesquisa(idPesquisa) {
  // Pega os dados da pesquisa da API, retornando uma promise que será resolvida por quem chamou.
  urlPesquisa = `${API_BASE}/pesquisa/${idPesquisa}`

  console.log(`a minha URL é ${urlPesquisa}`);
  return fetch(urlPesquisa) // pegar os dados..
  .then(retorno => retorno.json())
}

