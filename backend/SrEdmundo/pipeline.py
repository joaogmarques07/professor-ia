"""
Orquestrador de pipeline — lógica pura, sem HTTP.

Fluxo:
  arquivo_id → carrega bytes do disco → extrai texto (SK_HarryPotter)
             → executa skills na ordem → salva em conteudo_gerado → retorna ContextoPipeline

Para adicionar uma nova skill:
  1. Crie o módulo em skills/{tipo}/skill_nova.py
  2. Implemente _passo_nova(ctx, opcoes) abaixo
  3. Registre em _SKILLS_DISPONIVEIS
"""

import os
from modelos.tipos import ContextoPipeline
from base_conhecimento import banco
from skills.entrada.SK_HarryPotter import extrair


# ─── Registro de skills ───────────────────────────────────────────────────────
# Chave = nome usado na requisição. Valor = função _passo_*.
# Adicionar nova skill: incluir entrada aqui após implementar o _passo_.

_SKILLS_DISPONIVEIS: dict = {}  # preenchido ao final do arquivo


# ─── Ponto de entrada ─────────────────────────────────────────────────────────

def executar(arquivo_id: int, skills: list[str], opcoes: dict = {}) -> ContextoPipeline:
    """
    Executa o pipeline completo para um arquivo já salvo no repositório.

    Args:
        arquivo_id: ID do arquivo em banco.arquivos
        skills:     lista ordenada de skills a executar, ex: ["resumo", "slides"]
        opcoes:     parâmetros opcionais por skill, ex: {"resumo": {"nivel": "avancado"}}

    Returns:
        ContextoPipeline com texto_bruto, resultados e custo acumulado.

    Raises:
        ValueError: arquivo não encontrado ou skill desconhecida
        Exception:  erros internos de skill (propagados com contexto)
    """
    skills_invalidas = [s for s in skills if s not in _SKILLS_DISPONIVEIS]
    if skills_invalidas:
        raise ValueError(
            f"Skills desconhecidas: {skills_invalidas}. "
            f"Disponíveis: {list(_SKILLS_DISPONIVEIS.keys())}"
        )

    registro = banco.buscar_arquivo(arquivo_id)
    if not registro:
        raise ValueError(f"Arquivo {arquivo_id} não encontrado no banco.")

    caminho = registro["caminho"]
    if not os.path.exists(caminho):
        raise FileNotFoundError(
            f"Arquivo físico não encontrado em disco: {caminho}"
        )

    with open(caminho, "rb") as f:
        bytes_arquivo = f.read()

    ctx = ContextoPipeline(
        arquivo_id=arquivo_id,
        nome_arquivo=registro["nome_original"],
        bytes_arquivo=bytes_arquivo,
        area_id=registro["area_id"],
    )

    ctx = _passo_extrair(ctx)

    for skill in skills:
        opcoes_skill = opcoes.get(skill, {})
        try:
            ctx = _SKILLS_DISPONIVEIS[skill](ctx, opcoes_skill)
        except Exception as e:
            raise RuntimeError(f"Erro na skill '{skill}': {e}") from e

        banco.salvar_conteudo(
            arquivo_id=arquivo_id,
            tipo=skill,
            conteudo=ctx.resultados[skill],
            custo_brl=ctx.custo_brl,
        )

    return ctx


# ─── Passo fixo: extração ─────────────────────────────────────────────────────

def _passo_extrair(ctx: ContextoPipeline) -> ContextoPipeline:
    resultado = extrair(ctx.bytes_arquivo, ctx.nome_arquivo)
    ctx.texto_bruto = resultado.texto
    return ctx


# ─── Skills de processamento ──────────────────────────────────────────────────

def _passo_resumo(ctx: ContextoPipeline, opcoes: dict) -> ContextoPipeline:
    from skills.processamento.skill_resumo import gerar

    nivel  = opcoes.get("nivel", "intermediario")
    idioma = opcoes.get("idioma", "português")

    texto, tk_in, tk_out = gerar(ctx.texto_bruto, nivel, idioma)
    ctx.resultados["resumo"] = texto
    ctx.acumular_tokens(tk_in, tk_out)
    return ctx


# ─── Skills de saída ──────────────────────────────────────────────────────────

def _passo_slides(ctx: ContextoPipeline, opcoes: dict) -> ContextoPipeline:
    from skills.saida.skill_slides import do_resumo

    if "resumo" not in ctx.resultados:
        raise ValueError("skill 'slides' depende de 'resumo' — inclua 'resumo' antes na lista de skills.")

    html_bytes, _ = do_resumo(ctx.resultados["resumo"])
    ctx.resultados["slides"] = html_bytes.decode("utf-8")
    return ctx


# ─── Registro ─────────────────────────────────────────────────────────────────

_SKILLS_DISPONIVEIS = {
    "resumo": _passo_resumo,
    "slides": _passo_slides,
}
