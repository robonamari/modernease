function sortTable(e) {
  var tbody = document.querySelector("table tbody");
  var rows = Array.prototype.slice.call(tbody.rows);
  var isSameColumn = e === window.lastSortedColumnIndex;
  var defaultAsc = {
    1: true,
    2: false,
    3: false
  };
  var isAsc = isSameColumn ? window.lastSortOrder !== "asc" : (defaultAsc.hasOwnProperty(e) ? defaultAsc[e] : true);
  var sortedRows = rows.sort(function(a, b) {
    var aCell = a.cells[e];
    var bCell = b.cells[e];
    var aText = aCell && aCell.innerText ? aCell.innerText.toLowerCase() : "";
    var bText = bCell && bCell.innerText ? bCell.innerText.toLowerCase() : "";
    if (e === 2) { // Size
      aText = parseFloat(aText) || 0;
      bText = parseFloat(bText) || 0;
    } else if (e === 3) { // Last Modified
      var aTimeEl = aCell ? aCell.querySelector("time") : null;
      var bTimeEl = bCell ? bCell.querySelector("time") : null;
      var aTime = aTimeEl ? aTimeEl.getAttribute("datetime") : aText;
      var bTime = bTimeEl ? bTimeEl.getAttribute("datetime") : bText;
      aText = new Date(aTime).getTime() || 0;
      bText = new Date(bTime).getTime() || 0;
    }
    if (aText > bText) return isAsc ? 1 : -1;
    if (aText < bText) return isAsc ? -1 : 1;
    return 0;
  });
  tbody.innerHTML = "";
  for (var i = 0; i < sortedRows.length; i++) {
    tbody.appendChild(sortedRows[i]);
  }
  window.lastSortedColumnIndex = e;
  window.lastSortOrder = isAsc ? "asc" : "desc";
  for (var j = 0; j < sortedRows.length; j++) {
    var row = sortedRows[j];
    if (row.cells[1] && row.cells[1].innerText === "Parent Directory") {
      tbody.prepend(row);
      break;
    }
  }
}
