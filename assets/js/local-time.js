document.querySelectorAll(".local-time").forEach((t) => {
  const e = t.getAttribute("datetime");
  const n = new Date(e);
  if (!isNaN(n.getTime())) {
    t.textContent = n.toLocaleString();
  } else {
    t.textContent = "";
  }
});
