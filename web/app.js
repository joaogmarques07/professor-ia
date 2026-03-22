const API = "http://localhost:8000";

let abaAtiva = "texto";
let ultimoResumoId = null;
let custoTotal = 0;
let areaAtual = null;

// ── Navegação entre páginas ──────────────────────────────────────────────────
function navegarPara(pagina) {
  document.querySelectorAll(".nav-item").forEach(b => b.classList.remove("active"));
  const navBtn = document.querySelector(`.nav-item[data-page="${pagina}"]`);
  if (navBtn) navBtn.classList.add("active");
  document.querySelectorAll(".page").forEach(p => p.classList.add("hidden"));
  document.getElementById(`page-${pagina}`).classList.remove("hidden");
  if (pagina === "repositorio") carregarAreas();
  if (pagina === "inicio") carregarAreasInicio();
}

document.querySelectorAll(".nav-item").forEach(btn => {
  btn.addEventListener("click", () => navegarPara(btn.dataset.page));
});

// Botões de navegação na página Início
document.querySelectorAll("[data-page]").forEach(btn => {
  if (!btn.classList.contains("nav-item")) {
    btn.addEventListener("click", () => navegarPara(btn.dataset.page));
  }
});

// Carrega áreas no início
carregarAreasInicio();

async function carregarAreasInicio() {
  try {
    const res = await fetch(`${API}/repositorio/areas`);
    const areas = await res.json();
    const grid = document.getElementById("inicio-areas-grid");
    if (!areas.length) {
      grid.innerHTML = '<div class="empty-state" style="padding:20px 0">Nenhuma área criada ainda.<br><button class="btn-primary" style="margin-top:12px" onclick="navegarPara(\'repositorio\')">Criar primeira área</button></div>';
      return;
    }
    const icones = { pdf: "📄", docx: "📝", pptx: "📊", xlsx: "📗", txt: "📃" };
    grid.innerHTML = areas.slice(0, 6).map(a => `
      <div class="area-card" onclick="navegarPara('repositorio')" style="cursor:pointer">
        <div class="area-card-icon">🗂️</div>
        <div class="area-card-nome">${a.nome}</div>
        ${a.descricao ? `<div class="area-card-desc">${a.descricao}</div>` : ""}
      </div>
    `).join("");
  } catch {}
}

// ── Seleção rápida do repositório ────────────────────────────────────────────
document.getElementById("btn-abrir-selecao").addEventListener("click", async () => {
  const painel = document.getElementById("selecao-rapida");
  painel.classList.remove("hidden");
  const lista = document.getElementById("selecao-lista");
  lista.innerHTML = '<div style="color:var(--text-muted);font-size:13px">Carregando...</div>';
  try {
    const res = await fetch(`${API}/repositorio/arquivos/recentes`);
    const arquivos = await res.json();
    if (!arquivos.length) {
      lista.innerHTML = '<div style="color:var(--text-muted);font-size:13px">Nenhum arquivo com conteúdo gerado ainda.</div>';
      return;
    }
    const icones = { pdf: "📄", docx: "📝", pptx: "📊", xlsx: "📗", txt: "📃", mp3: "🎵", mp4: "🎬" };
    lista.innerHTML = arquivos.map(a => {
      const tipos = (a.tipos_gerados || "").split(",").filter(Boolean);
      const badges = tipos.map(t => `<span class="selecao-badge">${t}</span>`).join("");
      return `
        <div class="selecao-item" data-id="${a.id}" data-nome="${a.nome_original}">
          <span style="font-size:18px">${icones[a.tipo] || "📁"}</span>
          <div class="selecao-item-info">
            <div class="selecao-item-nome">${a.nome_original}</div>
            <div class="selecao-item-meta">${a.area_nome} · ${formatarData(a.criado_em)}</div>
          </div>
          <div class="selecao-item-badges">${badges}</div>
        </div>`;
    }).join("");

    lista.querySelectorAll(".selecao-item").forEach(item => {
      item.addEventListener("click", () => carregarArquivoNaTela(item.dataset.id, item.dataset.nome));
    });
  } catch {
    lista.innerHTML = '<div style="color:var(--text-muted);font-size:13px">Erro ao carregar.</div>';
  }
});

document.getElementById("btn-fechar-selecao").addEventListener("click", () => {
  document.getElementById("selecao-rapida").classList.add("hidden");
});

async function carregarArquivoNaTela(arquivoId, nome) {
  document.getElementById("selecao-rapida").classList.add("hidden");
  const conteudos = await (await fetch(`${API}/repositorio/arquivos/${arquivoId}/conteudo`)).json();
  const resumo = conteudos.find(c => c.tipo === "resumo");

  if (resumo) {
    document.getElementById("resultado-conteudo").innerHTML = marked.parse(resumo.conteudo);
    document.getElementById("custo-resumo-badge").textContent = `Carregado — ${nome}`;
    document.getElementById("resultado-resumo").classList.remove("hidden");
    document.getElementById("btn-slides").disabled = false;
    document.getElementById("btn-quiz").disabled = false;
    ultimoResumoId = null;
    document.getElementById("resultado-resumo").scrollIntoView({ behavior: "smooth", block: "start" });
  } else {
    alert("Este arquivo ainda não tem resumo. Gere pelo Repositório primeiro.");
  }
}

// ── Abas (Gerar) ─────────────────────────────────────────────────────────────
document.querySelectorAll(".tab").forEach(tab => {
  tab.addEventListener("click", () => {
    abaAtiva = tab.dataset.tab;
    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    tab.classList.add("active");
    document.getElementById("tab-texto").classList.toggle("hidden", abaAtiva !== "texto");
    document.getElementById("tab-arquivo").classList.toggle("hidden", abaAtiva !== "arquivo");
  });
});

// Upload drag & drop (Gerar)
const uploadArea = document.getElementById("upload-area");
const arquivoInput = document.getElementById("arquivo-input");
const uploadLabel = document.getElementById("upload-label");

uploadArea.addEventListener("click", () => arquivoInput.click());
arquivoInput.addEventListener("change", () => {
  const f = arquivoInput.files[0];
  if (f) { uploadLabel.textContent = f.name; uploadArea.classList.add("upload-selecionado"); }
});
uploadArea.addEventListener("dragover", e => { e.preventDefault(); uploadArea.classList.add("upload-drag"); });
uploadArea.addEventListener("dragleave", () => uploadArea.classList.remove("upload-drag"));
uploadArea.addEventListener("drop", e => {
  e.preventDefault();
  uploadArea.classList.remove("upload-drag");
  const f = e.dataTransfer.files[0];
  if (f) {
    const dt = new DataTransfer(); dt.items.add(f);
    arquivoInput.files = dt.files;
    uploadLabel.textContent = f.name;
    uploadArea.classList.add("upload-selecionado");
  }
});

// ── Gerar resumo (avulso) ─────────────────────────────────────────────────────
document.getElementById("btn-resumo").addEventListener("click", async () => {
  const btn = document.getElementById("btn-resumo");
  const txtEl = document.getElementById("btn-resumo-text");
  const loader = document.getElementById("btn-resumo-loader");
  setLoading(btn, txtEl, loader, "Gerando...", true);
  try {
    let data;
    const nivel = document.getElementById("nivel").value;

    if (abaAtiva === "texto") {
      const conteudo = document.getElementById("conteudo").value.trim();
      if (!conteudo) { document.getElementById("conteudo").focus(); return; }
      const res = await fetch(`${API}/gerar/resumo`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ conteudo, nivel }),
      });
      if (!res.ok) throw new Error((await res.json()).detail);
      data = await res.json();
    } else {
      const arquivo = arquivoInput.files[0];
      if (!arquivo) { alert("Selecione um arquivo."); return; }
      const form = new FormData();
      form.append("arquivo", arquivo);
      form.append("nivel", nivel);
      const res = await fetch(`${API}/gerar/resumo/pdf`, { method: "POST", body: form });
      if (!res.ok) throw new Error((await res.json()).detail);
      data = await res.json();
    }

    mostrarResumo(data);
  } catch (err) {
    alert(`Erro: ${err.message}`);
  } finally {
    setLoading(btn, txtEl, loader, "Gerar resumo", false);
  }
});

// ── Gerar quiz (avulso) ───────────────────────────────────────────────────────
document.getElementById("btn-quiz").addEventListener("click", async () => {
  const btn = document.getElementById("btn-quiz");
  const txtEl = document.getElementById("btn-quiz-text");
  const loader = document.getElementById("btn-quiz-loader");

  const conteudo = obterConteudoAtual();
  if (!conteudo) { alert("Gere um resumo primeiro ou cole um texto."); return; }

  setLoading(btn, txtEl, loader, "Gerando...", true);
  try {
    const res = await fetch(`${API}/gerar/quiz`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ conteudo }),
    });
    if (!res.ok) throw new Error((await res.json()).detail);
    const data = await res.json();
    mostrarQuiz(data);
  } catch (err) {
    alert(`Erro: ${err.message}`);
  } finally {
    setLoading(btn, txtEl, loader, "Gerar", false);
  }
});

function obterConteudoAtual() {
  const resumoEl = document.getElementById("resultado-conteudo");
  if (resumoEl && resumoEl.innerText.trim()) return resumoEl.innerText.trim();
  const textoEl = document.getElementById("conteudo");
  if (textoEl && textoEl.value.trim()) return textoEl.value.trim();
  return null;
}

function mostrarQuiz(data) {
  const q = data.quiz;
  const container = document.getElementById("resultado-quiz-conteudo");

  let html = `<div class="quiz-secao">`;
  html += `<div class="quiz-secao-titulo">Múltipla escolha</div>`;

  q.multipla_escolha.forEach((p, i) => {
    html += `
      <div class="quiz-pergunta" data-resposta="${p.resposta_correta}" data-idx="${i}">
        <div class="quiz-pergunta-texto">${i + 1}. ${p.pergunta}</div>
        <div class="quiz-opcoes">
          ${p.opcoes.map(o => `<button class="quiz-opcao" data-letra="${o[0]}">${o}</button>`).join("")}
        </div>
        <div class="quiz-explicacao">${p.explicacao}</div>
      </div>`;
  });

  html += `</div><div class="quiz-secao" style="margin-top:20px;">`;
  html += `<div class="quiz-secao-titulo">Perguntas abertas</div>`;

  q.abertas.forEach((p, i) => {
    html += `
      <div class="quiz-pergunta">
        <div class="quiz-pergunta-texto">${i + 1}. ${p.pergunta}</div>
        <div class="quiz-resposta-esperada">💡 <strong>Resposta esperada:</strong> ${p.resposta_esperada}</div>
      </div>`;
  });

  html += `</div>`;
  container.innerHTML = html;

  // Interatividade múltipla escolha
  container.querySelectorAll(".quiz-pergunta[data-resposta]").forEach(card => {
    const correta = card.dataset.resposta;
    card.querySelectorAll(".quiz-opcao").forEach(btn => {
      btn.addEventListener("click", () => {
        card.querySelectorAll(".quiz-opcao").forEach(b => b.disabled = true);
        const acertou = btn.dataset.letra === correta;
        btn.classList.add(acertou ? "correta" : "errada");
        if (!acertou) {
          card.querySelectorAll(".quiz-opcao").forEach(b => {
            if (b.dataset.letra === correta) b.classList.add("correta");
          });
        }
        card.querySelector(".quiz-explicacao").classList.add("visivel");
      });
    });
  });

  document.getElementById("custo-quiz-badge").textContent = `R$ ${data.custo.custo_brl.toFixed(4)}`;
  document.getElementById("resultado-quiz").classList.remove("hidden");
  document.getElementById("resultado-quiz").scrollIntoView({ behavior: "smooth", block: "start" });
  adicionarCusto("Quiz", data.custo.custo_brl);
}

document.getElementById("btn-copiar-quiz").addEventListener("click", () => {
  navigator.clipboard.writeText(document.getElementById("resultado-quiz-conteudo").innerText).then(() => {
    const btn = document.getElementById("btn-copiar-quiz");
    btn.textContent = "Copiado!";
    setTimeout(() => btn.textContent = "Copiar", 2000);
  });
});

// ── Gerar slides (avulso) ─────────────────────────────────────────────────────
document.getElementById("btn-slides").addEventListener("click", async () => {
  if (!ultimoResumoId) return;
  const btn = document.getElementById("btn-slides");
  const txtEl = document.getElementById("btn-slides-text");
  const loader = document.getElementById("btn-slides-loader");
  setLoading(btn, txtEl, loader, "Gerando...", true);
  try {
    const res = await fetch(`${API}/gerar/slides/do-resumo/${ultimoResumoId}`, { method: "POST" });
    if (!res.ok) throw new Error((await res.json()).detail);
    const html = await res.text();
    window.open(URL.createObjectURL(new Blob([html], { type: "text/html" })), "_blank");
    adicionarCusto("Slides", 0);
  } catch (err) {
    alert(`Erro: ${err.message}`);
  } finally {
    setLoading(btn, txtEl, loader, "Gerar", false);
  }
});

// ── Copiar ────────────────────────────────────────────────────────────────────
document.getElementById("btn-copiar").addEventListener("click", () => {
  navigator.clipboard.writeText(document.getElementById("resultado-conteudo").innerText).then(() => {
    const btn = document.getElementById("btn-copiar");
    btn.textContent = "Copiado!";
    setTimeout(() => btn.textContent = "Copiar", 2000);
  });
});

// ── Repositório: áreas ────────────────────────────────────────────────────────
async function carregarAreas() {
  try {
    const res = await fetch(`${API}/repositorio/areas`);
    const areas = await res.json();
    renderAreas(areas);
  } catch {
    document.getElementById("areas-grid").innerHTML = '<div class="empty-state">Erro ao carregar áreas.</div>';
  }
}

function renderAreas(areas) {
  const grid = document.getElementById("areas-grid");
  if (!areas.length) {
    grid.innerHTML = '<div class="empty-state">Nenhuma área criada ainda.<br>Clique em "+ Nova área" para começar.</div>';
    return;
  }
  grid.innerHTML = areas.map(a => `
    <div class="area-card" data-id="${a.id}" data-nome="${a.nome}" data-desc="${a.descricao || ''}">
      <div class="area-card-icon">🗂️</div>
      <div class="area-card-nome">${a.nome}</div>
      ${a.descricao ? `<div class="area-card-desc">${a.descricao}</div>` : ""}
    </div>
  `).join("");

  grid.querySelectorAll(".area-card").forEach(card => {
    card.addEventListener("click", () => abrirArea(card.dataset.id, card.dataset.nome, card.dataset.desc));
  });
}

// Nova área
document.getElementById("btn-nova-area").addEventListener("click", () => {
  document.getElementById("form-nova-area").classList.toggle("hidden");
  document.getElementById("input-area-nome").focus();
});

document.getElementById("btn-cancelar-area").addEventListener("click", () => {
  document.getElementById("form-nova-area").classList.add("hidden");
  document.getElementById("input-area-nome").value = "";
  document.getElementById("input-area-desc").value = "";
});

document.getElementById("btn-salvar-area").addEventListener("click", async () => {
  const nome = document.getElementById("input-area-nome").value.trim();
  if (!nome) { document.getElementById("input-area-nome").focus(); return; }
  const descricao = document.getElementById("input-area-desc").value.trim();
  try {
    const res = await fetch(`${API}/repositorio/areas`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nome, descricao }),
    });
    if (!res.ok) throw new Error((await res.json()).detail);
    document.getElementById("btn-cancelar-area").click();
    await carregarAreas();
  } catch (err) {
    alert(`Erro: ${err.message}`);
  }
});

// ── Repositório: arquivos ─────────────────────────────────────────────────────
async function abrirArea(id, nome, desc) {
  areaAtual = { id, nome, desc };
  document.getElementById("titulo-area-atual").textContent = nome;
  document.getElementById("desc-area-atual").textContent = desc || "";
  document.getElementById("vista-areas").classList.add("hidden");
  document.getElementById("vista-arquivos").classList.remove("hidden");
  await carregarArquivos(id);
}

document.getElementById("btn-voltar-areas").addEventListener("click", () => {
  document.getElementById("vista-arquivos").classList.add("hidden");
  document.getElementById("vista-areas").classList.remove("hidden");
  areaAtual = null;
});

async function carregarArquivos(areaId) {
  try {
    const res = await fetch(`${API}/repositorio/areas/${areaId}/arquivos`);
    const arquivos = await res.json();
    renderArquivos(arquivos);
  } catch {
    document.getElementById("arquivos-lista").innerHTML = '<div class="empty-state">Erro ao carregar arquivos.</div>';
  }
}

function renderArquivos(arquivos) {
  const lista = document.getElementById("arquivos-lista");
  if (!arquivos.length) {
    lista.innerHTML = '<div class="empty-state">Nenhum arquivo nesta área ainda.<br>Clique em "+ Subir arquivo" para começar.</div>';
    return;
  }
  const icones = { pdf: "📄", docx: "📝", pptx: "📊", xlsx: "📗", txt: "📃", md: "📃", mp3: "🎵", mp4: "🎬", wav: "🎵", m4a: "🎵" };
  lista.innerHTML = arquivos.map(a => `
    <div class="arquivo-item" data-id="${a.id}">
      <div class="arquivo-tipo">${icones[a.tipo] || "📁"}</div>
      <div class="arquivo-info">
        <div class="arquivo-nome">${a.nome_original}</div>
        <div class="arquivo-meta">${a.tipo.toUpperCase()} · ${a.tamanho_mb.toFixed(2)} MB · ${formatarData(a.criado_em)}</div>
      </div>
      <div class="arquivo-acoes">
        <button class="btn-secondary btn-aprender" data-id="${a.id}">🧠 Aprender</button>
        <button class="btn-secondary btn-gerar-resumo" data-id="${a.id}">📄 Resumo</button>
        <button class="btn-secondary btn-gerar-quiz" data-id="${a.id}">❓ Quiz</button>
        <button class="btn-secondary btn-gerar-glossario" data-id="${a.id}">📚 Glossário</button>
        <button class="btn-secondary btn-gerar-exercicios" data-id="${a.id}">✏️ Exercícios</button>
        <button class="btn-secondary btn-gerar-slides" data-id="${a.id}">🎞️ Slides</button>
        <button class="btn-secondary btn-gerar-narracao" data-id="${a.id}">🎙️ Narrar</button>
        <button class="btn-secondary btn-gerar-video" data-id="${a.id}">🎬 Vídeo</button>
        <button class="btn-primary btn-gerar-tudo" data-id="${a.id}">⚡ Gerar tudo</button>
        <label class="btn-secondary btn-substituir" title="Substituir arquivo">
          🔄
          <input type="file" class="input-substituir" data-id="${a.id}" accept=".pdf,.docx,.pptx,.xlsx,.txt,.md,.csv,.html,.mp3,.wav,.m4a,.mp4" hidden />
        </label>
        <button class="btn-secondary btn-deletar" data-id="${a.id}" title="Deletar arquivo">🗑️</button>
      </div>
    </div>
    <div class="conteudo-arquivo hidden" id="conteudo-${a.id}"></div>
  `).join("");

  // Carrega conteúdo já gerado de cada arquivo
  arquivos.forEach(a => carregarConteudoArquivo(a.id));

  lista.querySelectorAll(".btn-aprender").forEach(btn => {
    btn.addEventListener("click", () => aprenderArquivo(btn.dataset.id, btn));
  });
  lista.querySelectorAll(".btn-gerar-resumo").forEach(btn => {
    btn.addEventListener("click", () => gerarDoArquivo(btn.dataset.id, "resumo", btn));
  });
  lista.querySelectorAll(".btn-gerar-quiz").forEach(btn => {
    btn.addEventListener("click", () => gerarDoArquivo(btn.dataset.id, "quiz", btn));
  });
  lista.querySelectorAll(".btn-gerar-glossario").forEach(btn => {
    btn.addEventListener("click", () => gerarDoArquivo(btn.dataset.id, "glossario", btn));
  });
  lista.querySelectorAll(".btn-gerar-exercicios").forEach(btn => {
    btn.addEventListener("click", () => gerarDoArquivo(btn.dataset.id, "exercicios", btn));
  });
  lista.querySelectorAll(".btn-gerar-slides").forEach(btn => {
    btn.addEventListener("click", () => gerarSlidesArquivo(btn.dataset.id, btn));
  });
  lista.querySelectorAll(".btn-gerar-narracao").forEach(btn => {
    btn.addEventListener("click", () => gerarDoArquivo(btn.dataset.id, "narracao", btn));
  });
  lista.querySelectorAll(".btn-gerar-video").forEach(btn => {
    btn.addEventListener("click", () => gerarDoArquivo(btn.dataset.id, "video", btn));
  });
  lista.querySelectorAll(".btn-gerar-tudo").forEach(btn => {
    btn.addEventListener("click", () => gerarTudo(btn.dataset.id, btn));
  });

  lista.querySelectorAll(".btn-deletar").forEach(btn => {
    btn.addEventListener("click", async () => {
      if (!confirm("Deletar este arquivo e todo o conteúdo gerado?")) return;
      const res = await fetch(`${API}/repositorio/arquivos/${btn.dataset.id}`, { method: "DELETE" });
      if (res.ok) await carregarArquivos(areaAtual.id);
      else alert("Erro ao deletar.");
    });
  });

  lista.querySelectorAll(".input-substituir").forEach(input => {
    input.addEventListener("change", async (e) => {
      const arquivo = e.target.files[0];
      if (!arquivo) return;
      if (!confirm(`Substituir pelo arquivo "${arquivo.name}"? O conteúdo gerado será apagado.`)) return;
      const form = new FormData();
      form.append("arquivo", arquivo);
      const res = await fetch(`${API}/repositorio/arquivos/${input.dataset.id}`, { method: "PUT", body: form });
      if (res.ok) await carregarArquivos(areaAtual.id);
      else alert(`Erro: ${(await res.json()).detail}`);
      e.target.value = "";
    });
  });
}

async function aprenderArquivo(arquivoId, btn) {
  const original = btn.textContent;
  btn.disabled = true;
  btn.textContent = "Analisando...";
  try {
    const res = await fetch(`${API}/repositorio/arquivos/${arquivoId}/aprender`, { method: "POST" });
    if (!res.ok) throw new Error((await res.json()).detail);
    const data = await res.json();
    adicionarCusto("Aprender", data.custo_total_brl || 0);
    await carregarConteudoArquivo(arquivoId);
  } catch (err) {
    alert(`Erro: ${err.message}`);
  } finally {
    btn.disabled = false;
    btn.textContent = original;
  }
}

async function gerarDoArquivo(arquivoId, tipo, btn) {
  const original = btn.textContent;
  btn.disabled = true;
  btn.textContent = "Gerando...";
  try {
    const res = await fetch(`${API}/repositorio/arquivos/${arquivoId}/gerar/${tipo}`, { method: "POST" });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail);
    adicionarCusto(tipo, data.custo_total_brl || 0);
    await carregarConteudoArquivo(arquivoId);
  } catch (err) {
    alert(`Erro: ${err.message}`);
  } finally {
    btn.disabled = false;
    btn.textContent = original;
  }
}

async function gerarSlidesArquivo(arquivoId, btn) {
  const original = btn.textContent;
  btn.disabled = true;
  btn.textContent = "Gerando...";
  try {
    const res = await fetch(`${API}/repositorio/arquivos/${arquivoId}/gerar/slides`, { method: "POST" });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail);
    adicionarCusto("Slides", data.custo_total_brl || 0);
    await carregarConteudoArquivo(arquivoId);
  } catch (err) {
    alert(`Erro: ${err.message}`);
  } finally {
    btn.disabled = false;
    btn.textContent = original;
  }
}

async function gerarTudo(arquivoId, btn) {
  const original = btn.textContent;
  btn.disabled = true;
  btn.textContent = "Gerando tudo...";
  try {
    const res = await fetch(`${API}/repositorio/arquivos/${arquivoId}/gerar/tudo`, { method: "POST" });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail);
    const etapas = data.etapas_executadas?.join(", ") || "nenhuma";
    adicionarCusto("Gerar tudo", data.custo_total_brl || 0);
    await carregarConteudoArquivo(arquivoId);
    if (data.etapas_reusadas?.length) {
      console.log(`Reusadas: ${data.etapas_reusadas.join(", ")}`);
    }
  } catch (err) {
    alert(`Erro: ${err.message}`);
  } finally {
    btn.disabled = false;
    btn.textContent = original;
  }
}

async function carregarConteudoArquivo(arquivoId) {
  try {
    const res = await fetch(`${API}/repositorio/arquivos/${arquivoId}/conteudo`);
    const itens = await res.json();
    if (itens.length) renderConteudoArquivo(arquivoId, itens);
  } catch {}
}

function renderConteudoArquivo(arquivoId, itens) {
  const el = document.getElementById(`conteudo-${arquivoId}`);
  if (!el) return;
  el.classList.remove("hidden");

  // Ordem de exibição
  const ordem = ["aprender", "elaborar", "resumo", "quiz", "glossario", "exercicios", "slides", "narracao", "video"];
  const ordenados = [...itens].sort((a, b) => {
    const ia = ordem.indexOf(a.tipo);
    const ib = ordem.indexOf(b.tipo);
    return (ia === -1 ? 99 : ia) - (ib === -1 ? 99 : ib);
  });

  el.innerHTML = ordenados.map(item => {
    if (item.tipo === "aprender") {
      const k = JSON.parse(item.conteudo);
      const conceitos = (k.conceitos_chave || []).map(c => `<li><strong>${c.conceito}</strong> — ${c.definicao}</li>`).join("");
      const ordem = (k.ordem_de_aprendizado || []).join(" → ");
      return `<div class="conteudo-gerado-item">
        <div class="conteudo-gerado-header"><span class="badge-tipo">🧠 Aprender</span><span class="conteudo-data">${formatarData(item.criado_em)} · R$ ${(item.custo_brl || 0).toFixed(4)}</span></div>
        <div class="conteudo-gerado-body">
          <p><strong>Tema:</strong> ${k.tema_central || ""}</p>
          <p><strong>Nível:</strong> ${k.nivel_complexidade || ""} &nbsp;·&nbsp; <strong>Público:</strong> ${k.publico_ideal || ""}</p>
          ${conceitos ? `<p style="margin-top:8px"><strong>Conceitos-chave:</strong></p><ul style="padding-left:16px;margin-top:4px">${conceitos}</ul>` : ""}
          ${ordem ? `<p style="margin-top:8px"><strong>Ordem de aprendizado:</strong> ${ordem}</p>` : ""}
        </div>
      </div>`;
    }

    if (item.tipo === "elaborar") {
      const p = JSON.parse(item.conteudo);
      const sequencia = (p.sequencia_de_ensino || []).map(e => e.foco || e).join(" → ");
      const formatos = (p.formatos_recomendados || []).join(", ");
      return `<div class="conteudo-gerado-item">
        <div class="conteudo-gerado-header"><span class="badge-tipo">🎯 Plano Didático</span><span class="conteudo-data">${formatarData(item.criado_em)} · R$ ${(item.custo_brl || 0).toFixed(4)}</span></div>
        <div class="conteudo-gerado-body">
          <p><strong>Ângulo de entrada:</strong> ${p.angulo_de_entrada || ""}</p>
          ${p.narrativa_central ? `<p><strong>Narrativa central:</strong> ${p.narrativa_central}</p>` : ""}
          ${sequencia ? `<p><strong>Sequência:</strong> ${sequencia}</p>` : ""}
          ${formatos ? `<p><strong>Formatos recomendados:</strong> ${formatos}</p>` : ""}
        </div>
      </div>`;
    }

    if (item.tipo === "resumo") {
      return `<div class="conteudo-gerado-item">
        <div class="conteudo-gerado-header">
          <span class="badge-tipo">📄 Resumo</span>
          <div style="display:flex;gap:10px;align-items:center;">
            <span class="conteudo-data">${formatarData(item.criado_em)} · R$ ${(item.custo_brl || 0).toFixed(4)}</span>
            <button class="btn-ghost" style="font-size:11px;padding:2px 8px;" onclick="abrirSlidesDoResumo(${arquivoId})">🎞️ Slides</button>
          </div>
        </div>
        <div class="conteudo-gerado-body resultado-conteudo">${marked.parse(item.conteudo)}</div>
      </div>`;
    }

    if (item.tipo === "quiz") {
      const quiz = JSON.parse(item.conteudo);
      return `<div class="conteudo-gerado-item">
        <div class="conteudo-gerado-header"><span class="badge-tipo">❓ Quiz</span><span class="conteudo-data">${formatarData(item.criado_em)} · R$ ${(item.custo_brl || 0).toFixed(4)}</span></div>
        <div class="conteudo-gerado-body"><em style="color:var(--text-muted);font-size:13px">${quiz.multipla_escolha?.length || 0} perguntas de múltipla escolha · ${quiz.abertas?.length || 0} abertas</em></div>
      </div>`;
    }

    if (item.tipo === "glossario") {
      const termos = JSON.parse(item.conteudo);
      const html = termos.map(t => `
        <div class="glossario-item">
          <div class="glossario-termo">${t.termo}</div>
          <div class="glossario-def">${t.definicao}</div>
          ${t.exemplo ? `<div class="glossario-ex">Ex: ${t.exemplo}</div>` : ""}
        </div>`).join("");
      return `<div class="conteudo-gerado-item">
        <div class="conteudo-gerado-header"><span class="badge-tipo">📚 Glossário</span><span class="conteudo-data">${formatarData(item.criado_em)} · R$ ${(item.custo_brl || 0).toFixed(4)} · ${termos.length} termos</span></div>
        <div class="conteudo-gerado-body"><div class="glossario-lista">${html}</div></div>
      </div>`;
    }

    if (item.tipo === "exercicios") {
      const exercicios = JSON.parse(item.conteudo);
      const html = exercicios.map((e, i) => `
        <div class="exercicio-item">
          <div class="exercicio-titulo">${i + 1}. ${e.titulo} <span class="exercicio-nivel">${e.nivel}</span></div>
          <div class="exercicio-contexto">${e.contexto}</div>
          <div class="exercicio-tarefa"><strong>Tarefa:</strong> ${e.tarefa}</div>
          <div class="exercicio-criterios"><strong>Critérios:</strong> ${(e.criterios || []).join(" · ")}</div>
        </div>`).join("");
      return `<div class="conteudo-gerado-item">
        <div class="conteudo-gerado-header"><span class="badge-tipo">✏️ Exercícios</span><span class="conteudo-data">${formatarData(item.criado_em)} · R$ ${(item.custo_brl || 0).toFixed(4)} · ${exercicios.length} exercícios</span></div>
        <div class="conteudo-gerado-body">${html}</div>
      </div>`;
    }

    if (item.tipo === "slides") {
      return `<div class="conteudo-gerado-item">
        <div class="conteudo-gerado-header"><span class="badge-tipo">🎞️ Slides</span><span class="conteudo-data">${formatarData(item.criado_em)} · sem custo</span></div>
        <div class="conteudo-gerado-body">
          <button class="btn-secondary" onclick="abrirSlidesDoResumo(${arquivoId})">▶ Abrir apresentação</button>
        </div>
      </div>`;
    }

    if (item.tipo === "narracao") {
      return `<div class="conteudo-gerado-item">
        <div class="conteudo-gerado-header"><span class="badge-tipo">🎙️ Narração</span><span class="conteudo-data">${formatarData(item.criado_em)} · R$ ${(item.custo_brl || 0).toFixed(4)}</span></div>
        <div class="conteudo-gerado-body">
          <audio controls style="width:100%;margin-top:4px;">
            <source src="${API}/repositorio/arquivos/${arquivoId}/narracao" type="audio/mpeg">
          </audio>
        </div>
      </div>`;
    }

    if (item.tipo === "video") {
      return `<div class="conteudo-gerado-item">
        <div class="conteudo-gerado-header"><span class="badge-tipo">🎬 Vídeo Narrado</span><span class="conteudo-data">${formatarData(item.criado_em)} · R$ ${(item.custo_brl || 0).toFixed(4)}</span></div>
        <div class="conteudo-gerado-body">
          <button class="btn-secondary" onclick="abrirVideo(${arquivoId})">▶ Abrir apresentação narrada</button>
        </div>
      </div>`;
    }

    return "";
  }).join("");
}

async function abrirSlidesDoResumo(arquivoId) {
  try {
    const conteudos = await (await fetch(`${API}/repositorio/arquivos/${arquivoId}/conteudo`)).json();
    const slides = conteudos.find(c => c.tipo === "slides");
    if (!slides) { alert("Slides ainda não gerados para este arquivo."); return; }
    window.open(URL.createObjectURL(new Blob([slides.conteudo], { type: "text/html" })), "_blank");
  } catch (err) {
    alert(`Erro: ${err.message}`);
  }
}

async function abrirVideo(arquivoId) {
  try {
    const res = await fetch(`${API}/repositorio/arquivos/${arquivoId}/video`);
    if (!res.ok) throw new Error("Vídeo não encontrado.");
    const html = await res.text();
    window.open(URL.createObjectURL(new Blob([html], { type: "text/html" })), "_blank");
  } catch (err) {
    alert(`Erro: ${err.message}`);
  }
}

// Subir arquivo na área
document.getElementById("input-arquivo-area").addEventListener("change", async (e) => {
  const arquivo = e.target.files[0];
  if (!arquivo || !areaAtual) return;

  const lista = document.getElementById("arquivos-lista");
  lista.insertAdjacentHTML("afterbegin", `<div class="upload-loading" id="upload-loading"><div class="loader" style="border-top-color:var(--accent)"></div> Enviando ${arquivo.name}...</div>`);

  try {
    const form = new FormData();
    form.append("arquivo", arquivo);
    const res = await fetch(`${API}/repositorio/areas/${areaAtual.id}/arquivos`, { method: "POST", body: form });
    if (!res.ok) throw new Error((await res.json()).detail);
    await carregarArquivos(areaAtual.id);
  } catch (err) {
    alert(`Erro: ${err.message}`);
    document.getElementById("upload-loading")?.remove();
  }
  e.target.value = "";
});

// ── Helpers ───────────────────────────────────────────────────────────────────
function mostrarResumo(data) {
  ultimoResumoId = data.resumo_id;
  document.getElementById("resultado-conteudo").innerHTML = marked.parse(data.resumo);
  document.getElementById("custo-resumo-badge").textContent = `R$ ${data.custo.custo_brl.toFixed(4)}`;
  document.getElementById("resultado-resumo").classList.remove("hidden");
  document.getElementById("btn-slides").disabled = false;
  document.getElementById("btn-quiz").disabled = false;
  document.getElementById("resultado-resumo").scrollIntoView({ behavior: "smooth", block: "start" });
  adicionarCusto("Resumo", data.custo.custo_brl);
}

function adicionarCusto(skill, valor) {
  custoTotal += valor;
  document.getElementById("custo-total").textContent = `R$ ${custoTotal.toFixed(4)}`;
  const item = document.createElement("div");
  item.className = "custo-item";
  item.innerHTML = `<span>${skill}</span><span>R$ ${valor.toFixed(4)}</span>`;
  document.getElementById("custo-breakdown").appendChild(item);
}

function setLoading(btn, textEl, loaderEl, label, on) {
  btn.disabled = on;
  textEl.textContent = label;
  loaderEl.classList.toggle("hidden", !on);
}

function formatarData(iso) {
  const d = new Date(iso);
  return d.toLocaleDateString("pt-BR") + " " + d.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
}
