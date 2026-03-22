"""
Skill: Narrador
Objetivo : Converter texto em áudio narrado (MP3) usando OpenAI TTS.
Vozes    : alloy, echo, fable, onyx, nova, shimmer
Modelo   : tts-1 (barato) ou tts-1-hd (melhor qualidade)
Custo    : ~USD 0.015 por 1.000 caracteres (tts-1)
Restrição: máx 4.096 caracteres por chamada — textos maiores são divididos.
"""

import os
from io import BytesIO
from openai import OpenAI

MODELO = "tts-1"
VOZ = "nova"  # nova = feminina, clara. Outras: alloy, echo, fable, onyx, shimmer
MAX_CHARS = 4000


def gerar(texto: str, voz: str = VOZ) -> tuple[bytes, float]:
    """
    Converte texto em MP3.
    Retorna (audio_bytes, custo_usd).
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Divide o texto se for maior que o limite
    trechos = _dividir(texto, MAX_CHARS)
    partes = []

    for trecho in trechos:
        resposta = client.audio.speech.create(
            model=MODELO,
            voice=voz,
            input=trecho,
            response_format="mp3",
        )
        partes.append(resposta.content)

    audio_bytes = b"".join(partes)
    custo_usd = (len(texto) / 1000) * 0.015
    return audio_bytes, custo_usd


def _dividir(texto: str, max_chars: int) -> list[str]:
    """Divide o texto em trechos respeitando pontuação."""
    if len(texto) <= max_chars:
        return [texto]

    trechos = []
    while texto:
        if len(texto) <= max_chars:
            trechos.append(texto)
            break
        corte = texto.rfind(". ", 0, max_chars)
        if corte == -1:
            corte = max_chars
        else:
            corte += 1
        trechos.append(texto[:corte].strip())
        texto = texto[corte:].strip()

    return trechos
