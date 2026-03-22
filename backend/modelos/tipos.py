from pydantic import BaseModel
from typing import Literal, Optional
from dataclasses import dataclass, field


# Câmbio fixo — atualizar conforme necessário
USD_BRL = 5.80

# Preços Claude Sonnet 4.6 por milhão de tokens
PRECO_INPUT_USD  = 3.0
PRECO_OUTPUT_USD = 15.0


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


class RequisicaoQuiz(BaseModel):
    conteudo: str
    n_multipla: int = 5
    n_abertas: int = 3
    idioma: str = "português"


class RespostaQuiz(BaseModel):
    quiz: dict
    custo: CustoSkill


class RequisicaoResumo(BaseModel):
    conteudo: str
    nivel: Literal["basico", "intermediario", "avancado"] = "intermediario"
    idioma: str = "português"


class RespostaResumo(BaseModel):
    resumo_id: int
    resumo: str
    nivel: str
    custo: CustoSkill


# ─── Pipeline ─────────────────────────────────────────────────────────────────

@dataclass
class ContextoPipeline:
    """
    Estado compartilhado que flui entre os passos do pipeline.
    Cada skill recebe, preenche seu campo em `resultados` e devolve.
    """
    arquivo_id: int
    nome_arquivo: str
    bytes_arquivo: bytes
    area_id: int

    texto_bruto: str = ""
    resultados: dict = field(default_factory=dict)  # {"resumo": "...", "slides": "<html>..."}

    tokens_entrada: int = 0
    tokens_saida: int = 0

    @property
    def custo_brl(self) -> float:
        return CustoSkill.calcular(self.tokens_entrada, self.tokens_saida).custo_brl

    def acumular_tokens(self, tk_in: int, tk_out: int) -> None:
        self.tokens_entrada += tk_in
        self.tokens_saida += tk_out


class RespostaPipeline(BaseModel):
    arquivo_id: int
    area_id: int
    skills_executadas: list[str]
    resultados: dict[str, str]
    custo: CustoSkill
