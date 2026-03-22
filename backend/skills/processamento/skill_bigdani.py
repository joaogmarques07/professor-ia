"""
Skill: Aprender
Objetivo : Analisar o conteúdo bruto e estruturar o conhecimento pedagogicamente,
           identificando tema, conceitos-chave, nível de complexidade e a melhor
           forma de ensinar aquele material específico.
Saída    : ConhecimentoEstruturado — usado pelas skills de resumo, quiz e slides
           para gerar saídas de maior qualidade.
Modelo   : Claude Sonnet 4.6 (via motor)
"""

from skills.motor import chamar_json

_PROMPT = """Você é um especialista em pedagogia e estruturação de conhecimento.
Analise o conteúdo abaixo e retorne um JSON estruturado com o conhecimento extraído.

Responda SOMENTE com JSON válido, sem markdown, no formato exato:
{{
  "tema_central": "nome do tema principal",
  "resumo_executivo": "2-3 frases explicando do que se trata",
  "nivel_complexidade": "basico | intermediario | avancado",
  "publico_ideal": "para quem este conteúdo é mais relevante",
  "conceitos_chave": [
    {{
      "conceito": "nome do conceito",
      "definicao": "definição clara e simples",
      "importancia": "por que este conceito importa"
    }}
  ],
  "ordem_de_aprendizado": [
    "primeiro entender X",
    "depois Y",
    "por fim Z"
  ],
  "pontos_de_atencao": [
    "ponto que costuma gerar dúvida ou erro"
  ],
  "analogias_sugeridas": [
    "analogia que facilita a compreensão"
  ],
  "prerequisitos": [
    "o que o aluno precisa saber antes"
  ],
  "aplicacoes_praticas": [
    "como aplicar este conhecimento no dia a dia"
  ]
}}

CONTEÚDO:
{conteudo}"""


def aprender(conteudo: str, idioma: str = "português") -> tuple[dict, int, int]:
    """
    Analisa o conteúdo e retorna (conhecimento_estruturado, tokens_entrada, tokens_saida).
    """
    return chamar_json(
        system=f"Você é um especialista em pedagogia. Responda sempre em {idioma}. Responda SOMENTE com JSON válido.",
        prompt=_PROMPT.format(conteudo=conteudo),
    )
