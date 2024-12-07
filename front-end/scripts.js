console.log("Olá mundo!")

// Carregar os dados da API

const API_BASE = "http://127.0.0.1:8000"

function carregaListagemPesquisas() { 
  const requestPesquisas = new Request(`${API_BASE}/pesquisas`)

  fetch(requestPesquisas) // Pega os dados...
  .then(retorno => retorno.json())
  .then(dadosPesquisas => {
    
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
}

function atualizaTabelaPesquisas() { 

  idPesquisa = document.querySelector("#listaMeses").value;
  tabela = document.querySelector("#tabelaResultados").style.display = 'inline'

  cabecalhoTabela = document.querySelector("#cabecalhoTabela")
  conteudoTabela = document.querySelector("#conteudoTabela")

  // Limpar a tabela, definindo uma condição inicial
  cabecalhoTabela.innerHTML = ''
  conteudoTabela.innerHTML = ''

  console.log("Atualizando a tabela...");

  // Pega os dados da pesquisa da API, retornando uma promise que será resolvida por quem chamou.
  urlPesquisa = `${API_BASE}/pesquisa/${idPesquisa}`
  console.log(`a minha URL é ${urlPesquisa}`);
  fetch(urlPesquisa) // pegar os dados..
  .then(retorno => retorno.json())
  .then(
    retorno => { 
      colunas_tabela = Object.keys(retorno[0]).slice(1)  // O primeiro é sempre ID, pela estrutura da API, mas não será necessário

      // Construir o cabeçalho...
     
      cabecalhoTabela.innerHTML = '<tr>'
      colunas_tabela.map((coluna) => cabecalhoTabela.innerHTML += `<th>${coluna.replace("_", " ")}</th>`)
      cabecalhoTabela.innerHTML += '</tr>'

      retorno.forEach((linhaRetornada) => {
        console.log(linhaRetornada)
        html = "<tr>"
        colunas_tabela.map((coluna) => html += `<td> ${linhaRetornada[coluna] === null?"-":linhaRetornada[coluna]} </td>`)
        html += "</tr>"
        conteudoTabela.innerHTML += html;
      })
    }
  );


  
}


// definidas as funções, podemos começar o código

// carregar a listagem de pesquisas...
carregaListagemPesquisas()

// ... e então, quando o usuário escolher uma pesquisa, gerar a tabela
window.onload = function() { 
  document.querySelector("#listaMeses").onchange = function() {
    console.log(`Você escolheu a pesquisa ${document.querySelector("#listaMeses").value}`);
    atualizaTabelaPesquisas();
  }
  
  // carrega a última pesquisa (que é a primeira na lista de pesquisas)
  atualizaTabelaPesquisas();
}
