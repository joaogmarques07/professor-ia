"""
Skill: Vídeo Narrado
Objetivo : Gera uma apresentação HTML com slides + narração por slide.
           Cada slide tem áudio embutido (base64) que avança automaticamente.
           Resultado: arquivo HTML autocontido, sem dependências externas de áudio.
Custo    : OpenAI TTS (~USD 0.015 / 1000 chars) + Claude (roteiro)
"""

import os
import base64
from openai import OpenAI
from skills.motor import chamar

MODELO_TTS = "tts-1"
VOZ = "nova"

_SYSTEM_ROTEIRO = (
    "Você é um professor experiente narrando slides de uma apresentação. "
    "Fale de forma natural, direta e pedagógica. "
    "Máximo 4 frases curtas por slide. Não mencione que é um slide."
)

# ─── Roteiro por slide ────────────────────────────────────────────────────────

def _gerar_roteiro(slides: list[dict]) -> tuple[list[str], int, int]:
    """
    Para cada slide, gera uma narração curta (2-4 frases) via motor.
    Retorna (roteiros, total_tokens_in, total_tokens_out).
    """
    roteiros = []
    total_in = total_out = 0

    for slide in slides:
        pontos = "\n".join(f"- {p}" for p in slide["pontos"])
        prompt = (
            f"Slide: {slide['titulo']}\n"
            f"Conteúdo:\n{pontos}\n\n"
            "Escreva a narração deste slide."
        )
        texto, tk_in, tk_out = chamar(system=_SYSTEM_ROTEIRO, prompt=prompt, max_tokens=256)
        roteiros.append(texto.strip())
        total_in += tk_in
        total_out += tk_out

    return roteiros, total_in, total_out


# ─── TTS por trecho ───────────────────────────────────────────────────────────

def _narrar(texto: str) -> bytes:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    resposta = client.audio.speech.create(
        model=MODELO_TTS,
        voice=VOZ,
        input=texto[:4000],
        response_format="mp3",
    )
    return resposta.content


# ─── HTML com slides + áudio embutido ─────────────────────────────────────────

def _montar_html(titulo: str, slides: list[dict], audios_b64: list[str]) -> str:
    def slide_capa():
        audio_tag = (
            f'<audio id="audio-0" src="data:audio/mpeg;base64,{audios_b64[0]}" preload="auto"></audio>'
            if audios_b64 else ""
        )
        return f"""
        <section class="capa" data-audio="0">
          {audio_tag}
          <div class="capa-inner">
            <div class="logo-mark">✦</div>
            <h1>{titulo}</h1>
            <div class="linha-acento"></div>
            <p class="subtitulo">✦ Messi</p>
          </div>
        </section>"""

    def slide_conteudo(s, idx):
        itens = "".join(f"<li>{p}</li>" for p in s["pontos"])
        audio_tag = (
            f'<audio id="audio-{idx}" src="data:audio/mpeg;base64,{audios_b64[idx]}" preload="auto"></audio>'
            if idx < len(audios_b64) else ""
        )
        return f"""
        <section class="conteudo" data-audio="{idx}">
          {audio_tag}
          <h2>{s['titulo']}</h2>
          <ul>{itens}</ul>
        </section>"""

    slides_html = slide_capa()
    for i, s in enumerate(slides):
        if s["pontos"]:
            slides_html += slide_conteudo(s, i + 1)

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <title>{titulo}</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.css">
  <style>
    :root {{
      --bg: #0f0f0f; --surface: #1a1a1a; --border: #2e2e2e;
      --text: #e8e8e8; --muted: #888; --acento: #7c6af7;
    }}
    .reveal-viewport, .reveal, .reveal .slides {{ background: var(--bg); }}
    .reveal .slides section {{
      text-align: left; height: 100%;
      display: flex !important; flex-direction: column; justify-content: center;
      padding: 48px 64px; box-sizing: border-box;
    }}
    .capa {{ border-left: 4px solid var(--acento); }}
    .capa-inner {{ display: flex; flex-direction: column; gap: 16px; }}
    .logo-mark {{ font-size: 28px; color: var(--acento); }}
    .capa h1 {{ font-size: 2.6em; font-weight: 700; color: var(--text); letter-spacing: -1px; line-height: 1.15; margin: 0; }}
    .linha-acento {{ width: 64px; height: 3px; background: var(--acento); border-radius: 2px; }}
    .subtitulo {{ color: var(--muted); font-size: 0.9em; margin: 0; }}
    .conteudo {{ border-left: 4px solid var(--acento); }}
    .conteudo h2 {{ font-size: 1.6em; font-weight: 700; color: var(--acento); margin: 0 0 32px; letter-spacing: -0.3px; }}
    .conteudo ul {{ list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 18px; }}
    .conteudo ul li {{ color: var(--text); font-size: 1.1em; line-height: 1.5; padding-left: 24px; position: relative; }}
    .conteudo ul li::before {{ content: "›"; position: absolute; left: 0; color: var(--acento); font-weight: bold; }}
    .reveal .slide-number {{ background: transparent; color: var(--muted); font-size: 13px; }}
    .reveal .slides section.present {{ animation: fadeIn 0.3s ease; }}
    @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: none; }} }}

    /* Controles de áudio */
    #player-bar {{
      position: fixed; bottom: 0; left: 0; right: 0;
      background: var(--surface); border-top: 1px solid var(--border);
      display: flex; align-items: center; gap: 12px;
      padding: 10px 24px; z-index: 999;
    }}
    #player-bar button {{
      background: var(--acento); border: none; color: #fff;
      padding: 6px 16px; border-radius: 6px; cursor: pointer; font-size: 14px;
    }}
    #player-bar span {{ color: var(--muted); font-size: 13px; }}
    #progresso {{ flex: 1; height: 3px; background: var(--border); border-radius: 2px; overflow: hidden; }}
    #progresso-bar {{ height: 100%; background: var(--acento); width: 0%; transition: width 0.3s; }}
  </style>
</head>
<body>
  <div class="reveal">
    <div class="slides">
      {slides_html}
    </div>
  </div>

  <div id="player-bar">
    <button id="btn-play">▶ Narrar</button>
    <div id="progresso"><div id="progresso-bar"></div></div>
    <span id="status">Pronto</span>
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
      keyboard: true,
    }});

    let narrando = false;
    let audioAtual = null;

    function pararAudio() {{
      if (audioAtual) {{
        audioAtual.pause();
        audioAtual.currentTime = 0;
      }}
      narrando = false;
      document.getElementById("btn-play").textContent = "▶ Narrar";
      document.getElementById("status").textContent = "Pronto";
      document.getElementById("progresso-bar").style.width = "0%";
    }}

    function narrarSlideAtual() {{
      const idx = Reveal.getState().indexh;
      const audio = document.getElementById("audio-" + idx);
      if (!audio) {{ pararAudio(); return; }}

      audioAtual = audio;
      const total = Reveal.getTotalSlides();
      document.getElementById("status").textContent = "Slide " + (idx + 1) + " de " + total;
      document.getElementById("progresso-bar").style.width = ((idx + 1) / total * 100) + "%";

      audio.currentTime = 0;
      audio.play().then(() => {{
        audio.onended = () => {{
          if (!narrando) return;
          const prox = idx + 1;
          if (prox < total) {{
            Reveal.slide(prox);
            setTimeout(narrarSlideAtual, 400);
          }} else {{
            pararAudio();
            document.getElementById("status").textContent = "Concluído ✓";
          }}
        }};
      }}).catch(e => {{
        document.getElementById("status").textContent = "Erro ao reproduzir";
        narrando = false;
      }});
    }}

    document.getElementById("btn-play").addEventListener("click", () => {{
      if (narrando) {{
        pararAudio();
      }} else {{
        narrando = true;
        document.getElementById("btn-play").textContent = "⏹ Parar";
        Reveal.slide(0);
        setTimeout(narrarSlideAtual, 300);
      }}
    }});

    // Para a narração ao navegar manualmente
    Reveal.on("slidechanged", () => {{
      if (narrando && audioAtual) {{
        audioAtual.pause();
        audioAtual.currentTime = 0;
      }}
    }});
  </script>
</body>
</html>"""


# ─── Entrada pública ──────────────────────────────────────────────────────────

def do_resumo(resumo: str) -> tuple[bytes, str, float]:
    """
    Gera HTML com vídeo narrado a partir de um resumo.
    Retorna (html_bytes, nome_arquivo, custo_usd).
    """
    from skills.saida.skill_slides import _resumo_para_slides

    dados = _resumo_para_slides(resumo)
    titulo = dados["titulo"]
    slides = dados["slides"]

    # Gera roteiro por slide (Claude via motor)
    roteiros, _, _ = _gerar_roteiro(slides)

    # Narra cada trecho (OpenAI TTS)
    total_chars = 0
    audios_b64 = [""]  # índice 0 = slide capa (sem narração de conteúdo)
    for roteiro in roteiros:
        audio_bytes = _narrar(roteiro)
        audios_b64.append(base64.b64encode(audio_bytes).decode("utf-8"))
        total_chars += len(roteiro)

    # Substitui áudio da capa pelo do primeiro slide
    if len(audios_b64) > 1:
        audios_b64[0] = audios_b64[1]

    custo_usd = (total_chars / 1000) * 0.015
    html = _montar_html(titulo, slides, audios_b64)
    nome = titulo.replace(" ", "_")[:40] + "_video.html"

    return html.encode("utf-8"), nome, custo_usd
