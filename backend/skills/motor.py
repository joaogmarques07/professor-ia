"""
Motor — camada transversal de chamada ao Claude.

Lê a base de conhecimento (CONTEXTO, PEDAGOGIA, ESTILO, APRESENTACAO)
e injeta esse contexto em toda chamada. As skills só passam o que é delas.
"""

import os
import json
import anthropic
from pathlib import Path

_cliente = None
_base: str | None = None

MODELO = "claude-sonnet-4-6"
BASE_PATH = Path(__file__).parent.parent / "base_conhecimento"

_ARQUIVOS_BASE = [
    "CONTEXTO.md",
    "PEDAGOGIA.md",
    "IDENTIDADE.md",
    "APRESENTACAO.md",
]


def _get_cliente() -> anthropic.Anthropic:
    global _cliente
    if _cliente is None:
        _cliente = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    return _cliente


def _get_base() -> str:
    """Carrega e concatena os arquivos da base de conhecimento (lazy, uma vez)."""
    global _base
    if _base is None:
        partes = []
        for nome in _ARQUIVOS_BASE:
            caminho = BASE_PATH / nome
            if caminho.exists():
                partes.append(caminho.read_text(encoding="utf-8"))
        _base = "\n\n---\n\n".join(partes)
    return _base


def _montar_system(instrucao_skill: str) -> str:
    """Monta o system prompt: base de conhecimento + instrução específica da skill."""
    base = _get_base()
    return (
        f"{base}\n\n"
        "---\n\n"
        f"{instrucao_skill}"
    )


def chamar(
    system: str,
    prompt: str,
    max_tokens: int = 4096,
) -> tuple[str, int, int]:
    """
    Chama o Claude com contexto da base de conhecimento injetado.
    Retorna (texto, tokens_in, tokens_out).
    """
    cliente = _get_cliente()

    with cliente.messages.stream(
        model=MODELO,
        max_tokens=max_tokens,
        system=_montar_system(system),
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        final = stream.get_final_message()

    texto = next(b.text for b in final.content if b.type == "text")
    return texto, final.usage.input_tokens, final.usage.output_tokens


def chamar_json(
    system: str,
    prompt: str,
    max_tokens: int = 4096,
) -> tuple[dict | list, int, int]:
    """
    Chama o Claude e extrai JSON da resposta.
    Retorna (dados, tokens_in, tokens_out).
    """
    texto, tokens_in, tokens_out = chamar(system, prompt, max_tokens)

    inicio_obj = texto.find("{")
    inicio_arr = texto.find("[")

    if inicio_obj == -1 and inicio_arr == -1:
        raise ValueError(f"Resposta sem JSON válido: {texto[:300]}")

    if inicio_arr != -1 and (inicio_obj == -1 or inicio_arr < inicio_obj):
        inicio, fim = inicio_arr, texto.rfind("]")
    else:
        inicio, fim = inicio_obj, texto.rfind("}")

    if fim == -1 or fim < inicio:
        raise ValueError(f"JSON malformado: {texto[:300]}")

    return json.loads(texto[inicio:fim + 1]), tokens_in, tokens_out


def recarregar_base() -> None:
    """Força releitura dos arquivos da base. Útil após edições sem reiniciar."""
    global _base
    _base = None
