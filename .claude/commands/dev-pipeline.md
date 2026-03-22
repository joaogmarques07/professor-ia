# /dev-pipeline — Trabalhar com o pipeline de orquestração

Você é um assistente especializado no pipeline do Professor.ia.
Leia `backend/orquestrador/pipeline.py` antes de qualquer ação.

## O que você pode fazer

### 1. Mostrar o estado atual
Liste as skills registradas em `_SKILLS_DISPONIVEIS` e o fluxo atual:
- Quais skills existem
- Dependências entre elas (ex: slides depende de resumo)
- Skills ainda não implementadas (comparar com `docs/arquitetura.md`)

### 2. Adicionar um passo ao pipeline
Se o usuário quiser encadear uma skill nova ou existente:
- Verifique se a skill existe em `backend/skills/`
- Se não existir, instrua o usuário a usar `/dev-nova-skill` primeiro
- Se existir, adicione o `_passo_` e registre em `_SKILLS_DISPONIVEIS`

### 3. Ajustar opções de um passo
Cada `_passo_` recebe um dict `opcoes`. Mostre as opções disponíveis de cada skill e ajude o usuário a passar os valores certos na requisição:
```json
POST /pipeline/arquivos/{id}/processar
{
  "skills": ["resumo", "slides"],
  "opcoes": {
    "resumo": {"nivel": "avancado", "idioma": "português"}
  }
}
```

### 4. Diagnosticar erro no pipeline
Se o usuário colar uma mensagem de erro:
- Identifique em qual `_passo_` ocorreu (a RuntimeError sempre informa a skill)
- Verifique dependências faltando
- Verifique se o arquivo físico existe em `backend/data/arquivos/`
- Sugira como reproduzir o erro de forma isolada via `/gerar/resumo` ou `/gerar/resumo/arquivo`

## Regras ao editar pipeline.py

- Imports de skills ficam DENTRO dos `_passo_*`, nunca no topo do arquivo
- Todo `_passo_` que chama Claude API deve chamar `ctx.acumular_tokens(tk_in, tk_out)`
- Todo `_passo_` deve verificar dependências explicitamente e lançar `ValueError` com mensagem clara
- O dict `_SKILLS_DISPONIVEIS` fica sempre no final do arquivo
