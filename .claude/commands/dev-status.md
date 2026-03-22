# /dev-status — Relatório de estado do projeto

Leia os arquivos abaixo e monte um relatório claro do estado atual do projeto.

## Arquivos para ler
- `CLAUDE.md` — visão geral e convenções
- `docs/arquitetura.md` — skills planejadas e status
- `backend/orquestrador/pipeline.py` — skills implementadas no pipeline
- `backend/skills/` — módulos existentes

## Formato do relatório

### Pipeline atual
Liste as skills registradas em `_SKILLS_DISPONIVEIS` e o fluxo que elas formam.

### Skills implementadas
| Skill | Arquivo | Está no pipeline? |
|-------|---------|------------------|
| ...   | ...     | ✅ / ❌           |

### Skills planejadas (ainda não implementadas)
Liste o que está em `docs/arquitetura.md` mas não existe em código.

### Endpoints disponíveis
Liste os 3 grupos de rotas e o que cada um oferece:
- `/gerar/*` — teste direto
- `/repositorio/*` — gestão de arquivos
- `/pipeline/*` — fluxo completo

### Próximo passo sugerido
Com base no que está faltando, sugira a próxima skill mais útil de implementar e como fazer isso usando `/dev-nova-skill`.

### Como testar agora
Mostre a sequência mínima de chamadas para validar o pipeline de ponta a ponta:
1. Criar área → `POST /repositorio/areas`
2. Subir arquivo → `POST /repositorio/areas/{id}/arquivos`
3. Processar → `POST /pipeline/arquivos/{id}/processar`
4. Ver resultado no retorno JSON
