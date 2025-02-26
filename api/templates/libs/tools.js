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


