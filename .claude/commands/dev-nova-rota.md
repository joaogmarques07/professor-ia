# /dev-nova-rota — Criar novo endpoint na API

Você vai criar um novo endpoint FastAPI seguindo os padrões do projeto Professor.ia.

## Passo 1 — Coletar informações

Pergunte ao usuário:
1. **O que a rota faz?** (descrição livre)
2. **Método HTTP**: GET, POST, DELETE
3. **Prefixo**: `/repositorio`, `/pipeline` ou `/gerar` (teste direto)?
4. **Precisa de schema de request?** (body com campos)
5. **Precisa de schema de response?** (campos do retorno)

## Passo 2 — Decidir o arquivo correto

| Prefixo | Arquivo |
|---------|---------|
| `/repositorio` | `backend/orquestrador/rotas_repositorio.py` |
| `/pipeline` | `backend/orquestrador/rotas_pipeline.py` |
| `/gerar` | `backend/orquestrador/rotas.py` |

## Passo 3 — Criar schemas se necessário

Se a rota precisar de modelos novos, adicione em `backend/modelos/tipos.py` seguindo o padrão:

```python
class RequisicaoNova(BaseModel):
    campo: str
    outro_campo: int = 0  # com default se opcional

class RespostaNova(BaseModel):
    id: int
    resultado: str
    custo: CustoSkill  # incluir sempre que houver chamada à Claude API
```

## Passo 4 — Implementar o endpoint

Padrão obrigatório:
```python
@router.{metodo}("/{caminho}", response_model={ModeloResposta})
def {nome_funcao}({parametros}):
    """Descrição clara do que a rota faz."""
    # 1. Validar entrada (retornar 400 se inválida)
    # 2. Chamar skill ou pipeline
    # 3. Salvar no banco se aplicável
    # 4. Retornar modelo de resposta
```

Mapeamento de erros:
- Input inválido → `HTTPException(status_code=400, ...)`
- Recurso não encontrado → `HTTPException(status_code=404, ...)`
- Erro interno → `HTTPException(status_code=500, detail=str(e))`

Nunca use `except Exception` sem re-raise ou logging — capture erros específicos primeiro.

## Passo 5 — Confirmar

Liste os arquivos modificados e mostre o endpoint gerado com exemplo de chamada:
```
{MÉTODO} {rota completa}
{body de exemplo se POST}
```
