const API = "http://localhost:8000";

let abaAtiva = "texto";
let ultimoResumoId = null;
let custoTotal = 0;

const el = {
  conteudo:          document.getElementById("conteudo"),
  nivel:             document.getElementById("nivel"),
  tabTexto:          document.getElementById("tab-texto"),
  tabPdf:            document.getElementById("tab-pdf"),
  uploadArea:        document.getElementById("upload-area"),
  uploadLabel:       document.getElementById("upload-label"),
  arquivoPdf:        document.getElementById("arquivo-pdf"),
  btnResumo:         document.getElementById("btn-resumo"),
  btnResumoText:     document.getElementById("btn-resumo-text"),
  btnResumoLoader:   document.getElementById("btn-resumo-loader"),
  resultadoResumo:   document.getElementById("resultado-resumo"),
  resultadoConteudo: document.getElementById("resultado-conteudo"),
  custoResumoBadge:  document.getElementById("custo-resumo-badge"),
  btnCopiar:         document.getElementById("btn-copiar"),
  btnSlides:         document.getElementById("btn-slides"),
  btnSlidesText:     document.getElementById("btn-slides-text"),
  btnSlidesLoader:   document.getElementById("btn-slides-loader"),
  custoTotal:        document.getElementById("custo-total"),
  custoBreakdown:    document.getElementById("custo-breakdown"),
};

// Abas
document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    abaAtiva = tab.dataset.tab;
    document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
    tab.classList.add("active");
    el.tabTexto.classList.toggle("hidden", abaAtiva !== "texto");
    el.tabPdf.classList.toggle("hidden", abaAtiva !== "pdf");
  });
});

// Upload PDF
el.uploadArea.addEventListener("click", () => el.arquivoPdf.click());
el.arquivoPdf.addEventListener("change", () => {
  const arquivo = el.arquivoPdf.files[0];
  el.uploadLabel.textContent = arquivo ? arquivo.name : "Clique para selecionar ou arraste um PDF";
  el.uploadArea.classList.toggle("upload-selecionado", !!arquivo);
});
el.uploadArea.addEventListener("dragover", (e) => { e.preventDefault(); el.uploadArea.classList.add("upload-drag"); });
el.uploadArea.addEventListener("dragleave", () => el.uploadArea.classList.remove("upload-drag"));
el.uploadArea.addEventListener("drop", (e) => {
  e.preventDefault();
  el.uploadArea.classList.remove("upload-drag");
  const arquivo = e.dataTransfer.files[0];
  if (arquivo?.name.endsWith(".pdf")) {
    const dt = new DataTransfer();
    dt.items.add(arquivo);
    el.arquivoPdf.files = dt.files;
    el.uploadLabel.textContent = arquivo.name;
    el.uploadArea.classList.add("upload-selecionado");
  }
});

// Gerar resumo
el.btnResumo.addEventListener("click", async () => {
  setLoading(el.btnResumo, el.btnResumoText, el.btnResumoLoader, "Gerando...", true);
  try {
    let data;
    if (abaAtiva === "texto") {
      const conteudo = el.conteudo.value.trim();
      if (!conteudo) { el.conteudo.focus(); return; }
      const res = await fetch(`${API}/gerar/resumo`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ conteudo, nivel: el.nivel.value }),
      });
      if (!res.ok) throw new Error((await res.json()).detail);
      data = await res.json();
    } else {
      const arquivo = el.arquivoPdf.files[0];
      if (!arquivo) { alert("Selecione um PDF."); return; }
      const form = new FormData();
      form.append("arquivo", arquivo);
      form.append("nivel", el.nivel.value);
      const res = await fetch(`${API}/gerar/resumo/pdf`, { method: "POST", body: form });
      if (!res.ok) throw new Error((await res.json()).detail);
      data = await res.json();
    }
    mostrarResumo(data);
  } catch (err) {
    alert(`Erro: ${err.message}`);
  } finally {
    setLoading(el.btnResumo, el.btnResumoText, el.btnResumoLoader, "Gerar resumo", false);
  }
});

// Gerar slides
el.btnSlides.addEventListener("click", async () => {
  if (!ultimoResumoId) return;
  setLoading(el.btnSlides, el.btnSlidesText, el.btnSlidesLoader, "Gerando...", true);
  try {
    const res = await fetch(`${API}/gerar/slides/do-resumo/${ultimoResumoId}`, { method: "POST" });
    if (!res.ok) throw new Error((await res.json()).detail);
    const html = await res.text();
    const blob = new Blob([html], { type: "text/html" });
    window.open(URL.createObjectURL(blob), "_blank");
    adicionarCusto("Slides", 0);
  } catch (err) {
    alert(`Erro: ${err.message}`);
  } finally {
    setLoading(el.btnSlides, el.btnSlidesText, el.btnSlidesLoader, "Gerar", false);
  }
});

// Copiar
el.btnCopiar.addEventListener("click", () => {
  navigator.clipboard.writeText(el.resultadoConteudo.innerText).then(() => {
    el.btnCopiar.textContent = "Copiado!";
    setTimeout(() => (el.btnCopiar.textContent = "Copiar"), 2000);
  });
});

function mostrarResumo(data) {
  ultimoResumoId = data.resumo_id;
  el.resultadoConteudo.innerHTML = marked.parse(data.resumo);
  el.custoResumoBadge.textContent = `R$ ${data.custo.custo_brl.toFixed(4)}`;
  el.resultadoResumo.classList.remove("hidden");
  el.btnSlides.disabled = false;
  el.resultadoResumo.scrollIntoView({ behavior: "smooth", block: "start" });
  adicionarCusto("Resumo", data.custo.custo_brl);
}

function adicionarCusto(skill, valor) {
  custoTotal += valor;
  el.custoTotal.textContent = `R$ ${custoTotal.toFixed(4)}`;

  const item = document.createElement("div");
  item.className = "custo-item";
  item.innerHTML = `<span>${skill}</span><span>R$ ${valor.toFixed(4)}</span>`;
  el.custoBreakdown.appendChild(item);
}

function setLoading(btn, textEl, loaderEl, label, on) {
  btn.disabled = on;
  textEl.textContent = label;
  loaderEl.classList.toggle("hidden", !on);
}
