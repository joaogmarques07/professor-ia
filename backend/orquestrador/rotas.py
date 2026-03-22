"""
Rotas de teste direto — chamam skills isoladas sem passar pelo repositório.
Úteis para validar uma skill específica rapidamente.

Para o fluxo completo (arquivo → repositório → pipeline → conteúdo gerado),
use POST /pipeline/arquivos/{id}/processar
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import Response
from modelos.tipos import RequisicaoResumo, RespostaResumo, CustoSkill
from skills.processamento import skill_resumo
from skills.entrada.SK_HarryPotter import extrair, FORMATOS_SUPORTADOS
from skills.saida import skill_slides
from base_conhecimento import banco

router = APIRouter(prefix="/gerar", tags=["geração (teste direto)"])


@router.post("/resumo", response_model=RespostaResumo)
def criar_resumo(req: RequisicaoResumo):
    """Gera resumo a partir de texto bruto. Não requer arquivo no repositório."""
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


@router.post("/resumo/arquivo", response_model=RespostaResumo)
async def criar_resumo_de_arquivo(
    arquivo: UploadFile = File(...),
    nivel: str = Form("intermediario"),
    idioma: str = Form("português"),
):
    """
    Extrai texto de qualquer formato suportado e gera resumo.
    Não requer arquivo no repositório.
    Formatos aceitos: PDF, DOCX, PPTX, XLSX, TXT, MD, HTML, MP3, MP4...
    """
    nome = arquivo.filename
    extensao = "." + nome.rsplit(".", 1)[-1].lower() if "." in nome else ""

    if extensao not in FORMATOS_SUPORTADOS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato '{extensao}' não suportado. Aceitos: {', '.join(sorted(FORMATOS_SUPORTADOS))}",
        )

    try:
        conteudo_bytes = await arquivo.read()
        extraido = extrair(conteudo_bytes, nome)
        if not extraido.texto.strip():
            raise HTTPException(status_code=400, detail="Não foi possível extrair texto do arquivo.")
        texto, tk_in, tk_out = skill_resumo.gerar(extraido.texto, nivel, idioma)
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


@router.post("/slides/do-resumo/{resumo_id}")
def criar_slides_do_resumo(resumo_id: int):
    """Gera slides HTML a partir de um resumo salvo."""
    registro = banco.buscar_resumo(resumo_id)
    if not registro:
        raise HTTPException(status_code=404, detail="Resumo não encontrado.")
    try:
        html_bytes, _ = skill_slides.do_resumo(registro["resumo"])
        return Response(content=html_bytes, media_type="text/html; charset=utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
