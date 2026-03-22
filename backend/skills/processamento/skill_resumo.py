"""
Skill: Resumo
Objetivo : Gera resumos educacionais em 3 níveis de profundidade.
           Se receber 'plano' (saída do Elaborar), segue a estratégia didática.
           Se receber 'conhecimento' (saída do Aprender), gera com mais qualidade.
Saída    : texto em markdown
Modelo   : Claude Sonnet 4.6 (via motor)
"""

from skills.motor import chamar

_NIVEIS = {
    "basico": "simples e acessível, como se explicando para alguém sem conhecimento prévio",
    "intermediario": "claro e estruturado, com os principais conceitos bem explicados",
    "avancado": "técnico e aprofundado, mantendo detalhes e nuances importantes",
}


def gerar(
    conteudo: str,
    nivel: str = "intermediario",
    idioma: str = "português",
    conhecimento: dict = None,
    plano: dict = None,
) -> tuple[str, int, int]:
    """
    Retorna (resumo, tokens_entrada, tokens_saida).
    Prioridade: plano (Elaborar) > conhecimento (Aprender) > só o conteúdo.
    """
    descricao = _NIVEIS.get(nivel, _NIVEIS["intermediario"])

    if plano:
        sequencia = " → ".join(e["foco"] for e in plano.get("sequencia_de_ensino", []))
        prompt = (
            f"Crie um resumo {descricao} seguindo o plano didático abaixo.\n\n"
            f"PLANO DIDÁTICO:\n"
            f"- Ângulo de entrada: {plano.get('angulo_de_entrada', '')}\n"
            f"- Narrativa central: {plano.get('narrativa_central', '')}\n"
            f"- Sequência: {sequencia}\n"
            f"- Pontos críticos: {'; '.join(plano.get('pontos_criticos', []))}\n"
            f"- Armadilhas a evitar: {'; '.join(plano.get('armadilhas_comuns', []))}\n"
            f"- Metáforas úteis: {'; '.join(plano.get('metaforas_chave', []))}\n\n"
            f"CONTEÚDO ORIGINAL:\n{conteudo}\n\n"
            "Estruture com:\n"
            "- **Visão geral**\n"
            "- **Conceitos essenciais** (na sequência do plano)\n"
            "- **Pontos de atenção**\n"
            "- **Como aplicar**"
        )
    elif conhecimento:
        contexto = (
            f"Tema: {conhecimento.get('tema_central', '')}\n"
            f"Nível: {conhecimento.get('nivel_complexidade', '')}\n"
            f"Público: {conhecimento.get('publico_ideal', '')}\n"
            f"Conceitos-chave: {', '.join(c['conceito'] for c in conhecimento.get('conceitos_chave', []))}\n"
            f"Ordem de aprendizado: {' → '.join(conhecimento.get('ordem_de_aprendizado', []))}\n"
        )
        prompt = (
            f"Com base na análise pedagógica abaixo, crie um resumo {descricao}.\n\n"
            f"ANÁLISE PEDAGÓGICA:\n{contexto}\n\n"
            f"CONTEÚDO ORIGINAL:\n{conteudo}\n\n"
            "Estruture com:\n"
            "- **Visão geral**\n"
            "- **Conceitos essenciais** (na ordem de aprendizado)\n"
            "- **Pontos de atenção**\n"
            "- **Como aplicar**"
        )
    else:
        prompt = (
            f"Crie um resumo {descricao} do conteúdo abaixo.\n\n"
            "Estruture com:\n"
            "- **Visão geral** (2-3 frases)\n"
            "- **Pontos principais** (lista)\n"
            "- **Conclusão**\n\n"
            f"CONTEÚDO:\n{conteudo}"
        )

    return chamar(
        system=f"Você é um especialista em criar resumos educacionais. Sempre responda em {idioma}.",
        prompt=prompt,
    )
