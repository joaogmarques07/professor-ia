import re


def _resumo_para_slides(resumo: str) -> dict:
    linhas = resumo.strip().splitlines()
    slides = []
    titulo_apresentacao = "Apresentação"
    slide_atual = None

    for linha in linhas:
        linha = linha.strip()
        if not linha:
            continue

        match_header = re.match(r"^#{1,3}\s+\*?\*?(.+?)\*?\*?$", linha)
        match_bold   = re.match(r"^\*\*(.+?)\*\*\s*$", linha)

        if match_header or match_bold:
            if slide_atual:
                slides.append(slide_atual)
            titulo_secao = (match_header or match_bold).group(1).strip()
            if not slides and titulo_apresentacao == "Apresentação":
                titulo_apresentacao = titulo_secao
            slide_atual = {"titulo": titulo_secao, "pontos": []}

        elif linha.startswith(("- ", "* ", "• ")):
            ponto = re.sub(r"\*\*(.+?)\*\*", r"\1", linha.lstrip("-*• ").strip())
            if slide_atual and ponto:
                slide_atual["pontos"].append(ponto)

        else:
            texto = re.sub(r"\*\*(.+?)\*\*", r"\1", linha)
            if slide_atual and texto:
                for frase in re.split(r"(?<=[.!?])\s+", texto):
                    if frase.strip():
                        slide_atual["pontos"].append(frase.strip())

    if slide_atual:
        slides.append(slide_atual)

    for s in slides:
        s["pontos"] = s["pontos"][:5]

    return {"titulo": titulo_apresentacao, "slides": slides}


def _montar_html(dados: dict) -> str:
    def slide_capa():
        return f"""
        <section class="capa">
          <div class="capa-inner">
            <div class="logo-mark">✦</div>
            <h1>{dados['titulo']}</h1>
            <div class="linha-acento"></div>
            <p class="subtitulo">Professor.ia</p>
          </div>
        </section>"""

    def slide_conteudo(s):
        itens = "".join(f"<li>{p}</li>" for p in s["pontos"])
        return f"""
        <section class="conteudo">
          <h2>{s['titulo']}</h2>
          <ul>{itens}</ul>
        </section>"""

    slides_html = slide_capa()
    for s in dados["slides"]:
        if s["pontos"]:
            slides_html += slide_conteudo(s)

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <title>{dados['titulo']}</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.css">
  <style>
    :root {{
      --bg: #0f0f0f;
      --surface: #1a1a1a;
      --border: #2e2e2e;
      --text: #e8e8e8;
      --muted: #888;
      --acento: #7c6af7;
    }}

    .reveal-viewport, .reveal, .reveal .slides {{ background: var(--bg); }}

    .reveal .slides section {{
      text-align: left;
      height: 100%;
      display: flex !important;
      flex-direction: column;
      justify-content: center;
      padding: 48px 64px;
      box-sizing: border-box;
    }}

    /* Capa */
    .capa {{ border-left: 4px solid var(--acento); }}
    .capa-inner {{ display: flex; flex-direction: column; gap: 16px; }}
    .logo-mark {{ font-size: 28px; color: var(--acento); }}
    .capa h1 {{
      font-size: 2.6em;
      font-weight: 700;
      color: var(--text);
      letter-spacing: -1px;
      line-height: 1.15;
      margin: 0;
    }}
    .linha-acento {{
      width: 64px;
      height: 3px;
      background: var(--acento);
      border-radius: 2px;
    }}
    .subtitulo {{ color: var(--muted); font-size: 0.9em; margin: 0; }}

    /* Conteúdo */
    .conteudo {{ border-left: 4px solid var(--acento); }}
    .conteudo h2 {{
      font-size: 1.6em;
      font-weight: 700;
      color: var(--acento);
      margin: 0 0 32px;
      letter-spacing: -0.3px;
    }}
    .conteudo ul {{
      list-style: none;
      padding: 0;
      margin: 0;
      display: flex;
      flex-direction: column;
      gap: 18px;
    }}
    .conteudo ul li {{
      color: var(--text);
      font-size: 1.1em;
      line-height: 1.5;
      padding-left: 24px;
      position: relative;
    }}
    .conteudo ul li::before {{
      content: "›";
      position: absolute;
      left: 0;
      color: var(--acento);
      font-weight: bold;
    }}

    /* Numeração */
    .reveal .slide-number {{
      background: transparent;
      color: var(--muted);
      font-size: 13px;
    }}

    /* Animação */
    .reveal .slides section.present {{ animation: fadeIn 0.3s ease; }}
    @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: none; }} }}
  </style>
</head>
<body>
  <div class="reveal">
    <div class="slides">
      {slides_html}
    </div>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js"></script>
  <script>
    Reveal.initialize({{
      hash: true,
      slideNumber: "c/t",
      controls: true,
      progress: true,
      transition: "fade",
      transitionSpeed: "fast",
    }});
  </script>
</body>
</html>"""


def do_resumo(resumo: str) -> tuple[bytes, str]:
    dados = _resumo_para_slides(resumo)
    html = _montar_html(dados)
    nome = dados["titulo"].replace(" ", "_")[:40] + ".html"
    return html.encode("utf-8"), nome
