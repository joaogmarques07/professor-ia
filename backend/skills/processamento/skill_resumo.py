import os
import anthropic

_NIVEIS = {
    "basico": "simples e acessível, como se explicando para alguém sem conhecimento prévio",
    "intermediario": "claro e estruturado, com os principais conceitos bem explicados",
    "avancado": "técnico e aprofundado, mantendo detalhes e nuances importantes",
}


def gerar(conteudo: str, nivel: str = "intermediario", idioma: str = "português") -> tuple[str, int, int]:
    """Retorna (resumo, tokens_entrada, tokens_saida)."""
    descricao = _NIVEIS.get(nivel, _NIVEIS["intermediario"])
    cliente = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    with cliente.messages.stream(
        model="claude-opus-4-6",
        max_tokens=4096,
        system=f"Você é um especialista em criar resumos educacionais. Sempre responda em {idioma}.",
        messages=[{
            "role": "user",
            "content": (
                f"Crie um resumo {descricao} do conteúdo abaixo.\n\n"
                "Estruture o resumo com:\n"
                "- **Visão geral** (2-3 frases)\n"
                "- **Pontos principais** (lista)\n"
                "- **Conclusão**\n\n"
                f"CONTEÚDO:\n{conteudo}"
            )
        }]
    ) as stream:
        final = stream.get_final_message()

    texto = next(b.text for b in final.content if b.type == "text")
    return texto, final.usage.input_tokens, final.usage.output_tokens
