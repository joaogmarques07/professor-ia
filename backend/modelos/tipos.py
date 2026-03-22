from pydantic import BaseModel
from typing import Literal, Optional


# Câmbio fixo — atualizar conforme necessário
USD_BRL = 5.80

# Preços Claude Opus 4.6 por milhão de tokens
PRECO_INPUT_USD  = 15.0
PRECO_OUTPUT_USD = 75.0


class CustoSkill(BaseModel):
    tokens_entrada: int
    tokens_saida: int
    custo_brl: float

    @staticmethod
    def calcular(tokens_entrada: int, tokens_saida: int) -> "CustoSkill":
        custo_usd = (tokens_entrada * PRECO_INPUT_USD + tokens_saida * PRECO_OUTPUT_USD) / 1_000_000
        return CustoSkill(
            tokens_entrada=tokens_entrada,
            tokens_saida=tokens_saida,
            custo_brl=round(custo_usd * USD_BRL, 4),
        )


class Area(BaseModel):
    id: int
    nome: str
    descricao: str = ""
    criado_em: str


class RequisicaoArea(BaseModel):
    nome: str
    descricao: str = ""


class Arquivo(BaseModel):
    id: int
    area_id: int
    nome_original: str
    tipo: str
    tamanho_mb: float
    enviado_por: str = ""
    criado_em: str


class RequisicaoResumo(BaseModel):
    conteudo: str
    nivel: Literal["basico", "intermediario", "avancado"] = "intermediario"
    idioma: str = "português"


class RespostaResumo(BaseModel):
    resumo_id: int
    resumo: str
    nivel: str
    custo: CustoSkill
