"""
Skill: Exercícios Práticos
Objetivo : Gera exercícios aplicados a partir do conteúdo — foco em prática,
           não em memorização (para isso, use quiz).
           Se receber 'plano' (saída do Elaborar), segue a sequência de ensino
           e evita as armadilhas comuns.
Saída    : lista de dicts {titulo, contexto, tarefa, criterios, nivel}
Modelo   : Claude Sonnet 4.6 (via motor)
"""

from skills.motor import chamar_json

_NIVEIS = {
    "basico": "práticos e acessíveis, que qualquer iniciante consiga realizar",
    "intermediario": "que exijam compreensão real do conteúdo e alguma análise",
    "avancado": "complexos, que exijam síntese, crítica ou aplicação em novos contextos",
}

_PROMPT = """Com base no conteúdo abaixo, crie {n} exercícios {descricao_nivel}.

{contexto_plano}

Cada exercício deve ter:
- Um título claro
- Um contexto situacional (cenário real onde o conhecimento será aplicado)
- A tarefa a ser realizada (o que o aluno deve fazer)
- Critérios de avaliação (como saber se fez bem)
- O nível de dificuldade

Responda SOMENTE com JSON válido, sem markdown, no formato exato:
{{
  "exercicios": [
    {{
      "titulo": "título do exercício",
      "contexto": "situação ou cenário de aplicação",
      "tarefa": "o que o aluno deve fazer",
      "criterios": ["critério 1", "critério 2"],
      "nivel": "basico | intermediario | avancado"
    }}
  ]
}}

CONTEÚDO:
{conteudo}"""


def gerar(
    conteudo: str,
    n: int = 5,
    nivel: str = "intermediario",
    idioma: str = "português",
    plano: dict = None,
) -> tuple[list, int, int]:
    """
    Gera exercícios práticos a partir do conteúdo.
    Retorna (exercicios, tokens_entrada, tokens_saida).
    """
    descricao_nivel = _NIVEIS.get(nivel, _NIVEIS["intermediario"])

    if plano:
        sequencia = " → ".join(e["foco"] for e in plano.get("sequencia_de_ensino", []))
        contexto_plano = (
            "Siga o plano didático abaixo ao criar os exercícios:\n"
            f"- Sequência de ensino (respeite esta progressão): {sequencia}\n"
            f"- Armadilhas comuns (crie exercícios que forcem o aluno a superá-las): {'; '.join(plano.get('armadilhas_comuns', []))}\n"
            f"- Aplicações práticas sugeridas: {'; '.join(plano.get('metaforas_chave', []))}\n"
        )
    else:
        contexto_plano = ""

    dados, tokens_in, tokens_out = chamar_json(
        system=f"Você é um especialista em pedagogia. Responda sempre em {idioma}. Responda SOMENTE com JSON válido.",
        prompt=_PROMPT.format(
            conteudo=conteudo,
            n=n,
            descricao_nivel=descricao_nivel,
            contexto_plano=contexto_plano,
        ),
    )
    return dados.get("exercicios", []), tokens_in, tokens_out
