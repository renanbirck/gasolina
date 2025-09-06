console.log("Carregamos!")



// Algumas funções auxiliares que serão usadas no decorrer do código. 

// Dado uma tabela com o id tableID, retorna a coluna de número dado 
// por columnIndex. 
function getTableColumn(tableId, columnIndex) {
  const table = document.getElementById(tableId);
  const rows = table.querySelectorAll('tr');
  const columnData = [];
  
  rows.forEach(row => {
    const cells = row.querySelectorAll('td, th');
    if (cells.length > columnIndex) {
      columnData.push(cells[columnIndex].textContent);
    }
  });
  
  return columnData;
}

// Dado uma tabela com o id tableID, retorna os valores
// mínimo e máximo da coluna dada por columnIndex.
function getMinMaxFromTableColumn(tableId, columnIndex) {
  const columnData = getTableColumn(tableId, columnIndex);
  const numericData = columnData
    .map(value => parseFloat(value))
    .filter(value => !isNaN(value));
  
  const min = Math.min(...numericData);
  const max = Math.max(...numericData);
  
  return { min, max };
}