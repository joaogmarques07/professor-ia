import pdfplumber
from io import BytesIO


def extrair_texto(conteudo: bytes) -> str:
    texto = []
    with pdfplumber.open(BytesIO(conteudo)) as pdf:
        for pagina in pdf.pages:
            t = pagina.extract_text()
            if t:
                texto.append(t)
    return "\n\n".join(texto)
