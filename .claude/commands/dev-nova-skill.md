# /dev-nova-skill — Criar nova skill no pipeline

Você vai criar uma nova skill seguindo exatamente os padrões do projeto Professor.ia.

## Passo 1 — Coletar informações

Pergunte ao usuário:
1. **Nome da skill** (ex: `avaliacao`, `roteiro`, `tts`)
2. **Tipo**: `processamento` (gera texto a partir do texto bruto) ou `saida` (transforma resultado de outra skill num formato final)
3. **Chama a Claude API?** (sim/não)
4. **Depende de outra skill?** (ex: slides depende de resumo)
5. **Descrição em uma linha** do que a skill faz

## Passo 2 — Criar o módulo da skill

Crie o arquivo em `backend/skills/{tipo}/skill_{nome}.py`.

### Padrão para skills que chamam a Claude API (processamento):
```python
"""
Skill: {Descrição}
"""
import os
import anthropic


def gerar({parametros}) -> tuple[str, int, int]:
    """Retorna (resultado, tokens_entrada, tokens_saida)."""
    cliente = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    with cliente.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system="...",
        messages=[{"role": "user", "content": "..."}]
    ) as stream:
        final = stream.get_final_message()

    texto = next(b.text for b in final.content if b.type == "text")
    return texto, final.usage.input_tokens, final.usage.output_tokens
```

### Padrão para skills de saída (sem Claude API):
```python
"""
Skill: {Descrição}
"""

def gerar({parametros}) -> tuple[bytes, str]:
    """Retorna (conteudo_bytes, nome_arquivo)."""
    ...
```

Regras:
- Imports de bibliotecas pesadas (anthropic, pdfplumber, etc.) ficam DENTRO das funções, não no topo do arquivo
- Código e comentários em português
- Modelo padrão: `claude-sonnet-4-6`

## Passo 3 — Adicionar o _passo_ em pipeline.py

Abra `backend/orquestrador/pipeline.py` e adicione a função wrapper na seção correta:

```python
def _passo_{nome}(ctx: ContextoPipeline, opcoes: dict) -> ContextoPipeline:
    from skills.{tipo}.skill_{nome} import gerar

    # se depende de outra skill, validar antes:
    if "{dependencia}" not in ctx.resultados:
        raise ValueError("skill '{nome}' depende de '{dependencia}'.")

    # chamar a skill e preencher ctx.resultados
    resultado, tk_in, tk_out = gerar(ctx.{campo_de_entrada}, **opcoes_relevantes)
    ctx.resultados["{nome}"] = resultado
    ctx.acumular_tokens(tk_in, tk_out)  # apenas se chamar Claude API
    return ctx
```

## Passo 4 — Registrar em _SKILLS_DISPONIVEIS

No final de `pipeline.py`, adicionar ao dict:
```python
_SKILLS_DISPONIVEIS = {
    ...
    "{nome}": _passo_{nome},
}
```

## Passo 5 — Confirmar

Liste os arquivos criados/modificados e mostre como testar a skill nova via:
```
POST /pipeline/arquivos/{id}/processar
{"skills": ["{dependencia_se_houver}", "{nome}"]}
```
