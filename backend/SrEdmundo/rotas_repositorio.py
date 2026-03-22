import os
import json
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import Response
from modelos.tipos import Area, RequisicaoArea, Arquivo, CustoSkill
from skills.entrada.SK_HarryPotter import FORMATOS_SUPORTADOS
from base_conhecimento import banco
from SrEdmundo import orquestrador

router = APIRouter(prefix="/repositorio", tags=["repositório"])


# ─── Áreas ───────────────────────────────────────────────────────────────────

@router.post("/areas", response_model=Area)
def criar_area(req: RequisicaoArea):
    try:
        area_id = banco.criar_area(req.nome, req.descricao)
        return Area(**banco.buscar_area(area_id))
    except Exception as e:
        if "UNIQUE constraint" in str(e):
            raise HTTPException(status_code=400, detail=f"Já existe uma área com o nome '{req.nome}'.")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/areas", response_model=list[Area])
def listar_areas():
    return [Area(**a) for a in banco.listar_areas()]


# ─── Arquivos ─────────────────────────────────────────────────────────────────

@router.post("/areas/{area_id}/arquivos", response_model=Arquivo)
async def subir_arquivo(
    area_id: int,
    arquivo: UploadFile = File(...),
    enviado_por: str = Form(""),
):
    if not banco.buscar_area(area_id):
        raise HTTPException(status_code=404, detail="Área não encontrada.")

    nome = arquivo.filename
    extensao = "." + nome.rsplit(".", 1)[-1].lower() if "." in nome else ""

    if extensao not in FORMATOS_SUPORTADOS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato '{extensao}' não suportado. Aceitos: {', '.join(sorted(FORMATOS_SUPORTADOS))}"
        )
    try:
        conteudo_bytes = await arquivo.read()
        arquivo_id = banco.salvar_arquivo(
            area_id=area_id,
            nome_original=nome,
            tipo=extensao.lstrip("."),
            conteudo_bytes=conteudo_bytes,
            enviado_por=enviado_por,
        )
        return Arquivo(**banco.buscar_arquivo(arquivo_id))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/areas/{area_id}/arquivos", response_model=list[Arquivo])
def listar_arquivos(area_id: int):
    if not banco.buscar_area(area_id):
        raise HTTPException(status_code=404, detail="Área não encontrada.")
    return [Arquivo(**a) for a in banco.listar_arquivos(area_id)]


@router.get("/arquivos/recentes")
def arquivos_recentes():
    return banco.listar_arquivos_com_conteudo()


@router.delete("/arquivos/{arquivo_id}")
def deletar_arquivo(arquivo_id: int):
    if not banco.deletar_arquivo(arquivo_id):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado.")
    return {"ok": True}


@router.put("/arquivos/{arquivo_id}", response_model=Arquivo)
async def substituir_arquivo(arquivo_id: int, arquivo: UploadFile = File(...)):
    if not banco.buscar_arquivo(arquivo_id):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado.")
    nome = arquivo.filename
    extensao = "." + nome.rsplit(".", 1)[-1].lower() if "." in nome else ""
    if extensao not in FORMATOS_SUPORTADOS:
        raise HTTPException(status_code=400, detail=f"Formato '{extensao}' não suportado.")
    try:
        conteudo_bytes = await arquivo.read()
        banco.substituir_arquivo(arquivo_id, nome, extensao.lstrip("."), conteudo_bytes)
        return Arquivo(**banco.buscar_arquivo(arquivo_id))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/arquivos/{arquivo_id}/conteudo")
def listar_conteudo(arquivo_id: int):
    if not banco.buscar_arquivo(arquivo_id):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado.")
    return banco.listar_conteudo(arquivo_id)


# ─── Pipeline via orquestrador ────────────────────────────────────────────────

def _executar(arquivo_id: int, objetivo: str, opcoes: dict = None):
    """Helper comum — chama o orquestrador e trata erros."""
    try:
        return orquestrador.executar(arquivo_id, objetivo, opcoes)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/arquivos/{arquivo_id}/aprender")
def aprender_arquivo(arquivo_id: int):
    return _executar(arquivo_id, "aprender")


@router.post("/arquivos/{arquivo_id}/gerar/resumo")
def gerar_resumo(
    arquivo_id: int,
    nivel: str = "intermediario",
    revisar: bool = False,
    publico: str = "adultos em aprendizagem profissional",
):
    return _executar(arquivo_id, "resumo", {"nivel": nivel, "revisar": revisar, "publico": publico})


@router.post("/arquivos/{arquivo_id}/gerar/quiz")
def gerar_quiz(
    arquivo_id: int,
    revisar: bool = False,
    publico: str = "adultos em aprendizagem profissional",
):
    return _executar(arquivo_id, "quiz", {"revisar": revisar, "publico": publico})


@router.post("/arquivos/{arquivo_id}/gerar/glossario")
def gerar_glossario(
    arquivo_id: int,
    revisar: bool = False,
    publico: str = "adultos em aprendizagem profissional",
):
    return _executar(arquivo_id, "glossario", {"revisar": revisar, "publico": publico})


@router.post("/arquivos/{arquivo_id}/gerar/exercicios")
def gerar_exercicios(arquivo_id: int, nivel: str = "intermediario"):
    return _executar(arquivo_id, "exercicios", {"nivel": nivel})


@router.post("/arquivos/{arquivo_id}/gerar/slides")
def gerar_slides(arquivo_id: int):
    return _executar(arquivo_id, "slides")


@router.post("/arquivos/{arquivo_id}/gerar/narracao")
def gerar_narracao(arquivo_id: int):
    return _executar(arquivo_id, "narracao")


@router.post("/arquivos/{arquivo_id}/gerar/video")
def gerar_video(arquivo_id: int):
    return _executar(arquivo_id, "video")


@router.post("/arquivos/{arquivo_id}/gerar/tudo")
def gerar_tudo(
    arquivo_id: int,
    nivel: str = "intermediario",
    revisar: bool = True,
    publico: str = "adultos em aprendizagem profissional",
):
    """Gera todos os formatos em sequência — resumo, quiz, glossário, exercícios, slides, narração."""
    return _executar(arquivo_id, "tudo", {"nivel": nivel, "revisar": revisar, "publico": publico})


# ─── Servir arquivos gerados ──────────────────────────────────────────────────

@router.get("/arquivos/{arquivo_id}/narracao")
def obter_narracao(arquivo_id: int):
    conteudos = banco.listar_conteudo(arquivo_id)
    narracao = next((c for c in conteudos if c["tipo"] == "narracao"), None)
    if not narracao:
        raise HTTPException(status_code=404, detail="Narração não gerada ainda.")
    with open(narracao["conteudo"], "rb") as f:
        return Response(content=f.read(), media_type="audio/mpeg")


@router.get("/arquivos/{arquivo_id}/video")
def obter_video(arquivo_id: int):
    conteudos = banco.listar_conteudo(arquivo_id)
    video = next((c for c in conteudos if c["tipo"] == "video"), None)
    if not video:
        raise HTTPException(status_code=404, detail="Vídeo não gerado ainda.")
    return Response(content=video["conteudo"].encode("utf-8"), media_type="text/html; charset=utf-8")
