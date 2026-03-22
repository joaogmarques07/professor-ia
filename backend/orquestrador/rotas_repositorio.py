from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from modelos.tipos import Area, RequisicaoArea, Arquivo
from skills.entrada.SK_HarryPotter import extrair, FORMATOS_SUPORTADOS
from base_conhecimento import banco

router = APIRouter(prefix="/repositorio", tags=["repositório"])


# ─── Áreas ───────────────────────────────────────────────────────────────────

@router.post("/areas", response_model=Area)
def criar_area(req: RequisicaoArea):
    try:
        area_id = banco.criar_area(req.nome, req.descricao)
        area = banco.buscar_area(area_id)
        return Area(**area)
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
        registro = banco.buscar_arquivo(arquivo_id)
        return Arquivo(**registro)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/areas/{area_id}/arquivos", response_model=list[Arquivo])
def listar_arquivos(area_id: int):
    if not banco.buscar_area(area_id):
        raise HTTPException(status_code=404, detail="Área não encontrada.")
    return [Arquivo(**a) for a in banco.listar_arquivos(area_id)]
