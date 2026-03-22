from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import Response
from modelos.tipos import RequisicaoResumo, RespostaResumo, RequisicaoQuiz, RespostaQuiz, CustoSkill
from skills.processamento import skill_resumo, skill_quiz
from skills.entrada import SK_HarryPotter
from skills.saida import skill_slides, skill_video
from base_conhecimento import banco

router = APIRouter(prefix="/gerar", tags=["geração"])


@router.post("/resumo", response_model=RespostaResumo)
def criar_resumo(req: RequisicaoResumo):
    if not req.conteudo.strip():
        raise HTTPException(status_code=400, detail="Conteúdo não pode estar vazio.")
    try:
        texto, tk_in, tk_out = skill_resumo.gerar(req.conteudo, req.nivel, req.idioma)
        resumo_id = banco.salvar_resumo(texto, req.nivel)
        return RespostaResumo(
            resumo_id=resumo_id,
            resumo=texto,
            nivel=req.nivel,
            custo=CustoSkill.calcular(tk_in, tk_out),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resumo/pdf", response_model=RespostaResumo)
async def criar_resumo_pdf(
    arquivo: UploadFile = File(...),
    nivel: str = Form("intermediario"),
    idioma: str = Form("português"),
):
    if not arquivo.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Apenas arquivos PDF são aceitos.")
    try:
        conteudo_bytes = await arquivo.read()
        resultado = SK_HarryPotter.extrair(conteudo_bytes, arquivo.filename)
        conteudo = resultado.texto
        if not conteudo.strip():
            raise HTTPException(status_code=400, detail="Não foi possível extrair texto do PDF.")
        texto, tk_in, tk_out = skill_resumo.gerar(conteudo, nivel, idioma)
        resumo_id = banco.salvar_resumo(texto, nivel)
        return RespostaResumo(
            resumo_id=resumo_id,
            resumo=texto,
            nivel=nivel,
            custo=CustoSkill.calcular(tk_in, tk_out),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quiz", response_model=RespostaQuiz)
def criar_quiz(req: RequisicaoQuiz):
    if not req.conteudo.strip():
        raise HTTPException(status_code=400, detail="Conteúdo não pode estar vazio.")
    try:
        quiz, tk_in, tk_out = skill_quiz.gerar(req.conteudo, req.n_multipla, req.n_abertas, req.idioma)
        return RespostaQuiz(quiz=quiz, custo=CustoSkill.calcular(tk_in, tk_out))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/slides/do-resumo/{resumo_id}")
def criar_slides_do_resumo(resumo_id: int):
    registro = banco.buscar_resumo(resumo_id)
    if not registro:
        raise HTTPException(status_code=404, detail="Resumo não encontrado.")
    try:
        html_bytes, _ = skill_slides.do_resumo(registro["resumo"])
        return Response(content=html_bytes, media_type="text/html; charset=utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/video/do-resumo/{resumo_id}")
def criar_video_do_resumo(resumo_id: int):
    registro = banco.buscar_resumo(resumo_id)
    if not registro:
        raise HTTPException(status_code=404, detail="Resumo não encontrado.")
    try:
        html_bytes, nome, custo_usd = skill_video.do_resumo(registro["resumo"])
        return Response(
            content=html_bytes,
            media_type="text/html; charset=utf-8",
            headers={"X-Custo-USD": str(round(custo_usd, 4)), "X-Nome": nome},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
