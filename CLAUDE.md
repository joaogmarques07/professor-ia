# Professor.ia — CLAUDE.md

> Lido automaticamente pelo Claude Code em toda sessão.

## O Projeto

Plataforma que recebe arquivos (PDF, DOCX, áudio, vídeo...) e gera automaticamente material educacional — resumos, slides, exercícios, vídeos narrados. Funciona como um SharePoint inteligente com gerador de conteúdo integrado.

- Contexto de negócio completo: `backend/base_conhecimento/CONTEXTO.md`
- Arquitetura detalhada e status das skills: `docs/arquitetura.md`

---

## Estrutura do Repositório

```
professor-ia/
├── backend/                      # API FastAPI (Python)
│   ├── app.py                    # Ponto de entrada — registra todos os routers
│   ├── requirements.txt
│   ├── .env.example              # Copiar para .env e preencher as chaves
│   ├── orquestrador/
│   │   ├── pipeline.py           # Lógica de orquestração pura (sem HTTP)
│   │   ├── rotas_pipeline.py     # /pipeline — fluxo completo (arquivo → conteúdo)
│   │   ├── rotas_repositorio.py  # /repositorio — upload e gestão de arquivos
│   │   └── rotas.py              # /gerar — rotas de teste direto (skill isolada)
│   ├── skills/
│   │   ├── entrada/              # SK_HarryPotter — extrai texto de qualquer arquivo
│   │   ├── processamento/        # skill_resumo — gera resumos via Claude API
│   │   └── saida/                # skill_slides — gera slides HTML
│   ├── modelos/tipos.py          # Schemas Pydantic + ContextoPipeline
│   ├── base_conhecimento/
│   │   ├── banco.py              # SQLite — áreas, arquivos, conteúdo gerado
│   │   └── CONTEXTO.md           # Contexto de negócio do projeto
│   └── data/                     # Banco SQLite + arquivos enviados (gitignored)
├── web/                          # Frontend estático (HTML/JS/CSS — sem framework)
├── docs/
│   └── arquitetura.md            # Diagrama mermaid e tabela de status das skills
└── .claude/commands/             # Slash commands do Claude Code
```

---

## Como rodar o backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env              # preencher ANTHROPIC_API_KEY (e OPENAI_API_KEY para áudio)
uvicorn app:app --reload
```

- API: `http://localhost:8000`
- Docs interativos: `http://localhost:8000/docs`

Para um guia passo a passo interativo, use `/dev-setup`.

---

## Fluxo principal (ponta a ponta)

```
POST /repositorio/areas/{id}/arquivos   → salva arquivo no repositório
POST /pipeline/arquivos/{id}/processar  → extrai texto + executa skills + salva conteudo_gerado
```

O `pipeline.py` é o coração da arquitetura — lógica Python pura, sem HTTP.
Cada skill é encadeada via `_SKILLS_DISPONIVEIS` e opera sobre `ContextoPipeline`.

---

## API — Endpoints

### `/pipeline` — Fluxo completo

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/pipeline/arquivos/{id}/processar` | Executa pipeline sobre arquivo do repositório |
| GET | `/pipeline/skills` | Lista skills disponíveis no pipeline |

### `/repositorio` — Gestão de arquivos

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/repositorio/areas` | Cria uma nova área |
| GET | `/repositorio/areas` | Lista áreas cadastradas |
| POST | `/repositorio/areas/{id}/arquivos` | Upload de arquivo para uma área |
| GET | `/repositorio/areas/{id}/arquivos` | Lista arquivos de uma área |

### `/gerar` — Teste direto (skill isolada, sem repositório)

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/gerar/resumo` | Gera resumo de texto puro |
| POST | `/gerar/resumo/arquivo` | Extrai texto de arquivo e gera resumo |
| POST | `/gerar/slides/do-resumo/{id}` | Gera slides HTML a partir de um resumo salvo |

### Outros

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/health` | Verifica se a API está no ar |

---

## Banco de dados (SQLite)

Arquivo: `backend/data/professor.db` — criado automaticamente ao subir a API.

| Tabela | O que armazena |
|--------|---------------|
| `areas` | Setores/departamentos |
| `arquivos` | Arquivos originais enviados (metadados + caminho físico) |
| `conteudo_gerado` | Material gerado pela IA, vinculado a `arquivo_id` |
| `resumos` | Legado — compatibilidade com rotas `/gerar` |

Arquivos físicos ficam em `backend/data/arquivos/{area_id}/`.
Banco acessado sempre via funções em `banco.py` — nunca SQL direto nas rotas.

---

## Stack técnica

| Camada | Tecnologia |
|--------|-----------|
| Backend | FastAPI + Python 3.11+ |
| IA | Claude API (Anthropic) — modelo: `claude-sonnet-4-6` |
| Banco | SQLite via `banco.py` (sem ORM) |
| Frontend | HTML/JS/CSS estático (sem framework) |
| Transcrição áudio | OpenAI Whisper API |

---

## Convenções de código

- **Idioma**: código, comentários e mensagens em **português**
- **Skills**: cada skill é um módulo Python independente em `backend/skills/{tipo}/`
- **Imports lazy**: bibliotecas pesadas (anthropic, pdfplumber etc.) importadas dentro das funções, não no topo do arquivo
- **Pipeline**: toda skill nova precisa de um `_passo_` em `pipeline.py` e registro em `_SKILLS_DISPONIVEIS`
- **Contrato das skills de processamento**: retornam `tuple[str, int, int]` → (resultado, tokens_entrada, tokens_saida)
- **Contrato das skills de saída**: retornam `tuple[bytes, str]` → (conteudo_bytes, nome_arquivo)
- **Custo**: toda chamada à Claude API chama `ctx.acumular_tokens(tk_in, tk_out)`; retornar sempre `CustoSkill` na resposta HTTP
- **Banco**: acesso sempre via funções de `banco.py`; nunca instanciar conexão diretamente nas rotas

---

## Status das skills (backend)

| Skill | Arquivo | No pipeline? |
|-------|---------|-------------|
| Extrator de arquivos | `skills/entrada/SK_HarryPotter.py` | ✅ (passo fixo) |
| Resumo | `skills/processamento/skill_resumo.py` | ✅ |
| Slides HTML | `skills/saida/skill_slides.py` | ✅ |
| Avaliação / Quiz | — | 🔲 |
| Roteiro de vídeo | — | 🔲 |
| Corretor pedagógico | — | 🔲 |
| TTS / narração | — | 🔲 |
| Avatar | — | 🔲 Fase futura |

Para adicionar uma skill nova, use `/dev-nova-skill`.

---

## Slash commands (Claude Code)

### Desenvolvimento
| Comando | Descrição |
|---------|-----------|
| `/dev-nova-skill` | Cria nova skill + wrapper no pipeline + registro |
| `/dev-nova-rota` | Cria novo endpoint FastAPI + schemas Pydantic |
| `/dev-pipeline` | Inspeciona e edita o pipeline de orquestração |
| `/dev-status` | Relatório do estado atual do projeto |
| `/dev-setup` | Guia de setup para primeira vez |

### Produto (geração pedagógica)
| Comando | Descrição |
|---------|-----------|
| `/professor` | Orquestrador — ponto de entrada para qualquer tarefa pedagógica |
| `/aprender` | Extrai e estrutura conhecimento de um conteúdo |
| `/didatica` | Define a melhor forma pedagógica de ensinar o conteúdo |
| `/rascunho` | Gera ponto de partida quando o usuário não tem material |
| `/apresentacao` | Cria slides |
| `/avaliacao` | Cria exercícios e avaliações |
| `/roteiro` | Cria script de vídeo |
| `/biblioteca` | Salva conteúdo na base de conhecimento |

---

## Princípios que guiam as decisões

1. **Custo visível** — toda operação que consome API informa o custo estimado em BRL
2. **Simples primeiro** — construir o mínimo que funciona, depois escalar
3. **Arquivos preservados** — o original nunca é sobrescrito; o que a IA gera é adicional
4. **Atualização sem retrabalho** — quando o conteúdo-fonte muda, o material pode ser regerado
5. **Multi-formato** — o mesmo conhecimento entregue de formas diferentes para perfis diferentes
6. **Aprendizado, não só informação** — a saída deve ser pedagógica, não apenas um resumo
