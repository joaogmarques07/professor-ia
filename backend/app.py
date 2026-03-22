from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from SrEdmundo.rotas import router
from SrEdmundo.rotas_repositorio import router as router_repositorio
from base_conhecimento import banco

banco.inicializar()

app = FastAPI(title="Professor.ia API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(router_repositorio)


@app.get("/health")
def health():
    return {"status": "ok", "versao": "0.1.0"}
