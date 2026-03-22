"""
Skill: Elaborar
Posição  : Após Aprender, antes das skills de saída.
Objetivo : Recebe o conhecimento estruturado (output do Aprender) e produz
           um plano didático — a estratégia de ensino para aquele conteúdo.
           Todas as skills de saída seguem este plano em vez de decidirem sozinhas.
Saída    : dict com angulo_de_entrada, narrativa_central, sequencia_de_ensino,
           formatos_recomendados, metaforas_chave, pontos_criticos,
           armadilhas_comuns, nivel_recomendado
Modelo   : Claude Sonnet 4.6 (via motor)
"""

from skills.motor import chamar_json

_PROMPT = """Com base na análise pedagógica do conteúdo abaixo, crie um plano didático.

Seu objetivo é responder: dado o que sabemos sobre este conteúdo, qual é a melhor
forma de ensiná-lo? Este plano guiará todas as saídas geradas (resumo, quiz, slides, exercícios).

Responda SOMENTE com JSON válido, sem markdown, no formato exato:
{{
  "angulo_de_entrada": "por onde começar — o gancho que conecta o aluno ao tema antes de qualquer conceito",
  "narrativa_central": "o fio condutor de toda a explicação — a história que amarra os conceitos",
  "sequencia_de_ensino": [
    {{
      "etapa": 1,
      "foco": "o que ensinar nesta etapa",
      "justificativa": "por que esta ordem faz sentido pedagogicamente"
    }}
  ],
  "formatos_recomendados": ["resumo", "slides", "quiz", "exercicios", "glossario"],
  "metaforas_chave": [
    "analogia ou metáfora que facilita a compreensão de um conceito específico"
  ],
  "pontos_criticos": [
    "o que não pode ser pulado ou simplificado demais — base do entendimento"
  ],
  "armadilhas_comuns": [
    "onde o aluno costuma se perder, confundir ou desistir"
  ],
  "nivel_recomendado": "basico | intermediario | avancado"
}}

Sobre os formatos recomendados: inclua apenas os que realmente fazem sentido para este
conteúdo. Conteúdo muito visual pede slides. Conteúdo procedimental pede exercícios.
Conteúdo denso em termos técnicos pede glossário.

ANÁLISE DO CONTEÚDO:
{conhecimento}"""


def elaborar(conhecimento: dict, idioma: str = "português") -> tuple[dict, int, int]:
    """
    Gera um plano didático a partir do conhecimento estruturado (output do aprender).
    Retorna (plano_didatico, tokens_entrada, tokens_saida).
    """
    import json

    return chamar_json(
        system=f"Você é um especialista em design instrucional e didática aplicada. Responda sempre em {idioma}. Responda SOMENTE com JSON válido.",
        prompt=_PROMPT.format(conhecimento=json.dumps(conhecimento, ensure_ascii=False, indent=2)),
    )
