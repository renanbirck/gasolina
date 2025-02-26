// construir as linhas a serem plotadas no gráfico.  

// como a maioria dos postos só vende gasolinas, etanol, diesel e GNV,
// acho bem razoável presumir que não irá ter novas colunas. Talvez 
// se no futuro os postos virarem eletropostos, será necessário atualizar.

// 1. Pegar as etiquetas de cada gráfico
lineLabels = [...document.querySelectorAll("#tabelaPrecos th")].map((header) => header.innerHTML);
console.log(lineLabels)

// 2. Pegar as datas 

dateLabels = getTableColumn("tabelaPrecos", 0).slice(1).map((dateLabel) => dateLabel.trim()); 
console.log(dateLabels)

// 3. Construir o array com os datasets 

datasets = [];

for(currentChart = 1; currentChart < lineLabels.length; currentChart++) {
  currentDataset = {
    label: lineLabels[currentChart],
    data: getTableColumn("tabelaPrecos", currentChart).slice(1).map((value) => parseFloat(value)),
    borderWidth: 1
  }

  datasets.push(currentDataset);
}


const ctx = document.getElementById('graficoPrecos');
chart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: dateLabels,
    datasets: datasets
  },
  options: {
    responsive: true,
    aspectRatio: 1.5,
    maintainAspectRatio: true,
    scales: {
      y: {
        beginAtZero: false
      }
    }
  }
});

// Forçar a redimensionar quando trocar o tamanho da página 
window.addEventListener('resize', function() {
    chart.resize();
});


