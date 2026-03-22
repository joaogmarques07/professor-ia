from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from modelos.tipos import RespostaPipeline, CustoSkill
from SrEdmundo import pipeline
from base_conhecimento import banco

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


class RequisicaoPipeline(BaseModel):
    skills: list[str] = ["resumo", "slides"]
    opcoes: dict = {}


@router.post("/arquivos/{arquivo_id}/processar", response_model=RespostaPipeline)
def processar_arquivo(arquivo_id: int, req: RequisicaoPipeline):
    """
    Executa o pipeline completo sobre um arquivo já salvo no repositório.

    - Extrai o texto do arquivo
    - Executa as skills na ordem informada
    - Salva cada resultado em conteudo_gerado
    - Retorna os resultados com custo total
    """
    registro = banco.buscar_arquivo(arquivo_id)
    if not registro:
        raise HTTPException(status_code=404, detail=f"Arquivo {arquivo_id} não encontrado.")

    try:
        ctx = pipeline.executar(
            arquivo_id=arquivo_id,
            skills=req.skills,
            opcoes=req.opcoes,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return RespostaPipeline(
        arquivo_id=ctx.arquivo_id,
        area_id=ctx.area_id,
        skills_executadas=req.skills,
        resultados=ctx.resultados,
        custo=CustoSkill.calcular(ctx.tokens_entrada, ctx.tokens_saida),
    )


@router.get("/skills")
def listar_skills():
    """Retorna as skills disponíveis no pipeline."""
    return {"skills": list(pipeline._SKILLS_DISPONIVEIS.keys())}
