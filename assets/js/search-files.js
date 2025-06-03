function filterTable(filterText) {
  document.querySelectorAll("#fileTableBody tr").forEach(row => {
    row.cells[1].innerText.toLowerCase().includes(filterText.toLowerCase()) ?
      row.style.display = "" :
      row.style.display = "none";
  });
}
