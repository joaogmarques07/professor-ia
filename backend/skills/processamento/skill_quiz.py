"""
Skill: Quiz
Objetivo : Gera perguntas de múltipla escolha e abertas a partir do conteúdo.
           Se receber 'plano' (saída do Elaborar), foca nos pontos críticos
           e evita as armadilhas comuns.
Saída    : dict com titulo, multipla_escolha[], abertas[]
Modelo   : Claude Sonnet 4.6 (via motor)
"""

from skills.motor import chamar_json

_PROMPT_BASE = """Crie um quiz a partir do conteúdo abaixo.

{contexto_plano}

Responda SOMENTE com JSON válido, sem markdown, no formato exato:
{{
  "titulo": "título do tema avaliado",
  "multipla_escolha": [
    {{
      "pergunta": "texto da pergunta",
      "opcoes": ["A) texto", "B) texto", "C) texto", "D) texto"],
      "resposta_correta": "A",
      "explicacao": "por que esta é a resposta correta"
    }}
  ],
  "abertas": [
    {{
      "pergunta": "texto da pergunta aberta",
      "resposta_esperada": "elementos que uma boa resposta deve conter"
    }}
  ]
}}

Gere {n_multipla} perguntas de múltipla escolha e {n_abertas} perguntas abertas.

CONTEÚDO:
{conteudo}"""


def gerar(
    conteudo: str,
    n_multipla: int = 5,
    n_abertas: int = 3,
    idioma: str = "português",
    plano: dict = None,
) -> tuple[dict, int, int]:
    """Retorna (quiz_dict, tokens_entrada, tokens_saida)."""

    if plano:
        contexto_plano = (
            "Use o plano didático abaixo para focar as perguntas:\n"
            f"- Pontos críticos (priorize nas perguntas): {'; '.join(plano.get('pontos_criticos', []))}\n"
            f"- Armadilhas comuns (teste se o aluno as evita): {'; '.join(plano.get('armadilhas_comuns', []))}\n"
            f"- Sequência de ensino: {' → '.join(e['foco'] for e in plano.get('sequencia_de_ensino', []))}\n"
        )
    else:
        contexto_plano = ""

    return chamar_json(
        system=f"Você é um especialista em avaliação educacional. Responda sempre em {idioma}. Responda SOMENTE com JSON válido.",
        prompt=_PROMPT_BASE.format(
            conteudo=conteudo,
            n_multipla=n_multipla,
            n_abertas=n_abertas,
            contexto_plano=contexto_plano,
        ),
    )
