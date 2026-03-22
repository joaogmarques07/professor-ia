"""
Skill: Revisar
Posição  : Entre processamento e saída — refina o output antes de apresentar.
Objetivo : Recebe o conteúdo gerado (resumo, quiz, glossário, etc.) e devolve
           uma versão pedagogicamente melhor, sem alterar o formato nem a estrutura.
Regra    : Se recebeu markdown → devolve markdown. Se recebeu JSON → devolve JSON.
Modelo   : Claude Sonnet 4.6 (via motor)
"""

from skills.motor import chamar, chamar_json

_SYSTEM = """Sua única função é receber um conteúdo já gerado e devolvê-lo revisado —
mais claro, mais ensinável, mais bem estruturado — sem mudar seu formato nem sua estrutura.

O que você deve fazer:
- Corrigir erros conceituais, linguísticos e de lógica
- Eliminar ambiguidades e repetições
- Reorganizar ideias em ordem melhor para entendimento
- Simplificar sem distorcer
- Melhorar fluidez e transição entre ideias
- Preservar a essência e intenção do conteúdo original

O que você NÃO deve fazer:
- Mudar o formato (markdown continua markdown, JSON continua JSON)
- Alterar a estrutura (campos, seções, chaves)
- Inventar conteúdo que não estava no original
- Expandir para além do que foi recebido
- Adicionar explicações teóricas ou comentários

Aplique os princípios de forma invisível. Entregue apenas o conteúdo revisado."""

_INSTRUCOES = {
    "resumo": (
        "Você está revisando um RESUMO educacional em formato markdown.\n"
        "Melhore a clareza, fluidez e didática. Mantenha os títulos, seções e markdown.\n"
        "Devolva APENAS o resumo revisado em markdown."
    ),
    "quiz": (
        "Você está revisando um QUIZ em formato JSON.\n"
        "Melhore as perguntas, opções e explicações — mais claros e bem formulados.\n"
        "Mantenha EXATAMENTE a mesma estrutura JSON (mesmos campos, mesmo número de itens).\n"
        "Devolva SOMENTE o JSON revisado, sem markdown."
    ),
    "glossario": (
        "Você está revisando um GLOSSÁRIO em formato JSON.\n"
        "Melhore as definições e exemplos — mais claros, precisos e acessíveis.\n"
        "Mantenha EXATAMENTE a estrutura JSON com os campos 'termo', 'definicao' e 'exemplo'.\n"
        "Devolva SOMENTE o JSON revisado, sem markdown."
    ),
    "exercicios": (
        "Você está revisando EXERCÍCIOS PRÁTICOS em formato JSON.\n"
        "Melhore o contexto, a tarefa e os critérios — mais claros, aplicáveis e bem formulados.\n"
        "Mantenha EXATAMENTE a estrutura JSON de cada exercício.\n"
        "Devolva SOMENTE o JSON revisado, sem markdown."
    ),
    "flashcards": (
        "Você está revisando FLASHCARDS em formato JSON.\n"
        "Melhore a frente (pergunta/conceito) e o verso (resposta) de cada cartão.\n"
        "Mantenha EXATAMENTE a estrutura JSON com os campos 'frente' e 'verso'.\n"
        "Devolva SOMENTE o JSON revisado, sem markdown."
    ),
}

_TIPOS_JSON = {"quiz", "glossario", "exercicios", "flashcards"}


def revisar(conteudo: str, tipo: str, publico: str = "adultos em aprendizagem profissional", idioma: str = "português") -> tuple[str, int, int]:
    """
    Revisa pedagogicamente o conteúdo gerado antes de enviar para apresentação.
    Retorna (conteudo_revisado, tokens_entrada, tokens_saida).
    """
    instrucao = _INSTRUCOES.get(tipo, (
        "Você está revisando um conteúdo educacional.\n"
        "Melhore clareza, lógica e didática. Preserve o formato original.\n"
        "Devolva apenas o conteúdo revisado."
    ))

    system = f"{_SYSTEM}\n\nSempre responda em {idioma}."
    prompt = f"Público-alvo: {publico}\n\n{instrucao}\n\nCONTEÚDO PARA REVISAR:\n{conteudo}"

    if tipo in _TIPOS_JSON:
        dados, tokens_in, tokens_out = chamar_json(system=system, prompt=prompt)
        import json
        return json.dumps(dados, ensure_ascii=False), tokens_in, tokens_out

    return chamar(system=system, prompt=prompt)
