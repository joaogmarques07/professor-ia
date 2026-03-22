"""
Skill: Glossário
Objetivo : Extrai e define os termos-chave do conteúdo em formato de glossário estruturado.
           Útil como referência rápida e para alinhar vocabulário antes do estudo.
Saída    : lista de dicts {termo, definicao, exemplo}
Modelo   : Claude Sonnet 4.6 (via motor)
"""

from skills.motor import chamar_json

_PROMPT = """Analise o conteúdo abaixo e extraia os principais termos técnicos ou conceituais.

Para cada termo forneça:
- Uma definição clara e acessível
- Um exemplo de uso ou aplicação prática (quando possível)

Responda SOMENTE com JSON válido, sem markdown, no formato exato:
{{
  "glossario": [
    {{
      "termo": "nome do termo",
      "definicao": "definição clara e objetiva",
      "exemplo": "exemplo de uso ou aplicação (ou vazio se não aplicável)"
    }}
  ]
}}

Extraia entre 8 e 20 termos, priorizando os mais relevantes e específicos do tema.

CONTEÚDO:
{conteudo}"""


def gerar(conteudo: str, idioma: str = "português") -> tuple[list, int, int]:
    """
    Extrai glossário do conteúdo.
    Retorna (termos, tokens_entrada, tokens_saida).
    """
    dados, tokens_in, tokens_out = chamar_json(
        system=f"Você é um especialista em criar glossários educacionais. Responda sempre em {idioma}. Responda SOMENTE com JSON válido.",
        prompt=_PROMPT.format(conteudo=conteudo),
    )
    return dados.get("glossario", []), tokens_in, tokens_out
