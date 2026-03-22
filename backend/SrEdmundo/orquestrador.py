"""
Orquestrador — pipeline central do Professor.ia.

Dado um arquivo e um objetivo, resolve dependências, reusa o que já existe
e executa apenas o que falta. As rotas viram chamadas de 2 linhas.

Fluxo:
    SK_HarryPotter → aprender → elaborar → [resumo, quiz, glossario, exercicios]
                                                   ↓
                                            [slides, narracao, video]
"""

import json
import os
from modelos.tipos import CustoSkill
from base_conhecimento import banco
from skills.entrada.SK_HarryPotter import extrair
from skills.processamento import (
    skill_bigdani,
    skill_elaborar,
    skill_resumo,
    skill_quiz,
    skill_glossario,
    skill_exercicios,
    skill_revisar,
)
from skills.saida import skill_slides, skill_narrador, skill_video

AUDIOS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "audios")

# ─── Grafo de dependências ────────────────────────────────────────────────────
#
# Cada objetivo define a sequência mínima de etapas necessárias.
# Etapas entre [] são opcionais — executadas se ainda não existirem no banco.
#
_PIPELINES = {
    "aprender":   ["extrair", "aprender", "elaborar"],
    "resumo":     ["extrair", "aprender", "elaborar", "resumo"],
    "quiz":       ["extrair", "aprender", "elaborar", "quiz"],
    "glossario":  ["extrair", "glossario"],
    "exercicios": ["extrair", "aprender", "elaborar", "exercicios"],
    "slides":     ["extrair", "aprender", "elaborar", "resumo", "slides"],
    "narracao":   ["extrair", "aprender", "elaborar", "resumo", "narracao"],
    "video":      ["extrair", "aprender", "elaborar", "resumo", "video"],
    "tudo":       ["extrair", "aprender", "elaborar", "resumo", "quiz", "glossario", "exercicios", "slides", "narracao"],
}


# ─── Executor de cada etapa ───────────────────────────────────────────────────

def _executar_etapa(
    etapa: str,
    arquivo_id: int,
    ctx: dict,
    opcoes: dict,
) -> tuple[any, float]:
    """
    Executa uma etapa do pipeline.
    ctx contém os resultados das etapas anteriores.
    Retorna (resultado, custo_brl).
    """
    texto = ctx.get("texto_bruto", "")
    revisar = opcoes.get("revisar", False)
    publico = opcoes.get("publico", "adultos em aprendizagem profissional")
    nivel = opcoes.get("nivel", "intermediario")
    idioma = opcoes.get("idioma", "português")

    if etapa == "extrair":
        registro = banco.buscar_arquivo(arquivo_id)
        with open(registro["caminho"], "rb") as f:
            conteudo_bytes = f.read()
        resultado = extrair(conteudo_bytes, registro["nome_original"])
        ctx["texto_bruto"] = resultado.texto
        return resultado.texto, 0.0

    elif etapa == "aprender":
        conhecimento, tk_in, tk_out = skill_bigdani.aprender(texto, idioma=idioma)
        ctx["aprender"] = conhecimento
        custo = CustoSkill.calcular(tk_in, tk_out)
        banco.salvar_conteudo(arquivo_id, "aprender", json.dumps(conhecimento, ensure_ascii=False), custo.custo_brl)
        return conhecimento, custo.custo_brl

    elif etapa == "elaborar":
        conhecimento = ctx.get("aprender", {})
        plano, tk_in, tk_out = skill_elaborar.elaborar(conhecimento, idioma=idioma)
        ctx["elaborar"] = plano
        custo = CustoSkill.calcular(tk_in, tk_out)
        banco.salvar_conteudo(arquivo_id, "elaborar", json.dumps(plano, ensure_ascii=False), custo.custo_brl)
        return plano, custo.custo_brl

    elif etapa == "resumo":
        texto_resumo, tk_in, tk_out = skill_resumo.gerar(
            texto,
            nivel=nivel,
            idioma=idioma,
            conhecimento=ctx.get("aprender"),
            plano=ctx.get("elaborar"),
        )
        custo_brl = CustoSkill.calcular(tk_in, tk_out).custo_brl
        if revisar:
            texto_resumo, r_in, r_out = skill_revisar.revisar(texto_resumo, "resumo", publico, idioma)
            custo_brl = round(custo_brl + CustoSkill.calcular(r_in, r_out).custo_brl, 4)
        ctx["resumo"] = texto_resumo
        banco.salvar_conteudo(arquivo_id, "resumo", texto_resumo, custo_brl)
        return texto_resumo, custo_brl

    elif etapa == "quiz":
        quiz, tk_in, tk_out = skill_quiz.gerar(texto, idioma=idioma, plano=ctx.get("elaborar"))
        custo_brl = CustoSkill.calcular(tk_in, tk_out).custo_brl
        quiz_str = json.dumps(quiz, ensure_ascii=False)
        if revisar:
            quiz_str, r_in, r_out = skill_revisar.revisar(quiz_str, "quiz", publico, idioma)
            custo_brl = round(custo_brl + CustoSkill.calcular(r_in, r_out).custo_brl, 4)
            quiz = json.loads(quiz_str)
        banco.salvar_conteudo(arquivo_id, "quiz", json.dumps(quiz, ensure_ascii=False), custo_brl)
        return quiz, custo_brl

    elif etapa == "glossario":
        termos, tk_in, tk_out = skill_glossario.gerar(texto, idioma=idioma)
        custo_brl = CustoSkill.calcular(tk_in, tk_out).custo_brl
        termos_str = json.dumps(termos, ensure_ascii=False)
        if revisar:
            termos_str, r_in, r_out = skill_revisar.revisar(termos_str, "glossario", publico, idioma)
            custo_brl = round(custo_brl + CustoSkill.calcular(r_in, r_out).custo_brl, 4)
            termos = json.loads(termos_str)
        banco.salvar_conteudo(arquivo_id, "glossario", json.dumps(termos, ensure_ascii=False), custo_brl)
        return termos, custo_brl

    elif etapa == "exercicios":
        exercicios, tk_in, tk_out = skill_exercicios.gerar(texto, nivel=nivel, idioma=idioma, plano=ctx.get("elaborar"))
        custo_brl = CustoSkill.calcular(tk_in, tk_out).custo_brl
        banco.salvar_conteudo(arquivo_id, "exercicios", json.dumps(exercicios, ensure_ascii=False), custo_brl)
        return exercicios, custo_brl

    elif etapa == "slides":
        resumo = ctx.get("resumo", "")
        html_bytes, _ = skill_slides.do_resumo(resumo)
        banco.salvar_conteudo(arquivo_id, "slides", html_bytes.decode("utf-8"), 0.0)
        return html_bytes, 0.0

    elif etapa == "narracao":
        resumo = ctx.get("resumo", "")
        audio_bytes, custo_usd = skill_narrador.gerar(resumo)
        custo_brl = round(custo_usd * 5.80, 4)
        os.makedirs(AUDIOS_PATH, exist_ok=True)
        audio_path = os.path.join(AUDIOS_PATH, f"arquivo_{arquivo_id}.mp3")
        with open(audio_path, "wb") as f:
            f.write(audio_bytes)
        banco.salvar_conteudo(arquivo_id, "narracao", audio_path, custo_brl)
        return audio_path, custo_brl

    elif etapa == "video":
        resumo = ctx.get("resumo", "")
        html_bytes, nome, custo_usd = skill_video.do_resumo(resumo)
        custo_brl = round(custo_usd * 5.80, 4)
        banco.salvar_conteudo(arquivo_id, "video", html_bytes.decode("utf-8"), custo_brl)
        return html_bytes, custo_brl

    raise ValueError(f"Etapa desconhecida: {etapa}")


# ─── Ponto de entrada ─────────────────────────────────────────────────────────

def executar(
    arquivo_id: int,
    objetivo: str,
    opcoes: dict = None,
) -> dict:
    """
    Executa o pipeline para um arquivo e objetivo.

    objetivo: "resumo" | "quiz" | "glossario" | "exercicios" |
              "slides" | "narracao" | "video" | "aprender" | "tudo"

    opcoes: {
        revisar: bool = False,
        nivel: str = "intermediario",
        idioma: str = "português",
        publico: str = "adultos em aprendizagem profissional",
    }

    Retorna: {
        "resultados": {etapa: resultado},
        "custo_total_brl": float,
        "etapas_executadas": [str],
        "etapas_reusadas": [str],
    }
    """
    if not banco.buscar_arquivo(arquivo_id):
        raise ValueError(f"Arquivo {arquivo_id} não encontrado.")

    if objetivo not in _PIPELINES:
        raise ValueError(f"Objetivo '{objetivo}' inválido. Use: {list(_PIPELINES.keys())}")

    opcoes = opcoes or {}
    etapas = _PIPELINES[objetivo]

    # Carrega o que já foi gerado para este arquivo
    ja_gerado = {c["tipo"]: c["conteudo"] for c in banco.listar_conteudo(arquivo_id)}

    # Contexto compartilhado entre etapas
    ctx = {}

    # Pré-carrega dependências já existentes no contexto
    for tipo in ("aprender", "elaborar", "resumo"):
        if tipo in ja_gerado:
            try:
                ctx[tipo] = json.loads(ja_gerado[tipo])
            except Exception:
                ctx[tipo] = ja_gerado[tipo]

    resultados = {}
    custo_total = 0.0
    executadas = []
    reusadas = []

    for etapa in etapas:
        if etapa != "extrair" and etapa in ja_gerado:
            # Reusa — não regera
            reusadas.append(etapa)
            try:
                resultados[etapa] = json.loads(ja_gerado[etapa])
            except Exception:
                resultados[etapa] = ja_gerado[etapa]
            continue

        resultado, custo = _executar_etapa(etapa, arquivo_id, ctx, opcoes)
        resultados[etapa] = resultado
        custo_total = round(custo_total + custo, 4)
        executadas.append(etapa)

    return {
        "resultados": resultados,
        "custo_total_brl": custo_total,
        "etapas_executadas": executadas,
        "etapas_reusadas": reusadas,
    }
