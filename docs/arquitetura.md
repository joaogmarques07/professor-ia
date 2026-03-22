# Professor.ia — Arquitetura

**Última revisão:** Março 2026

---

## Visão Geral

Plataforma que recebe qualquer conteúdo, aprende com ele e gera material educacional automaticamente em múltiplos formatos. Funciona também como repositório centralizado por área — o arquivo original nunca é perdido.

```
┌─────────────────────────────────────────────────────────────┐
│  CAMADA 3 — PLATAFORMA (web/)                               │
│  Frontend: HTML + JS + CSS                                  │
│  Duas páginas: "Gerar" (avulso) e "Repositório"             │
│  Custo visível por operação, total acumulado na sessão       │
├─────────────────────────────────────────────────────────────┤
│  CAMADA 2 — GERADOR (backend/)                              │
│  FastAPI · Skills · Motor · Orquestrador                    │
│  Pipeline: Extrair → Aprender → Elaborar → Gerar → Entregar │
├─────────────────────────────────────────────────────────────┤
│  CAMADA 1 — REPOSITÓRIO                                     │
│  SQLite · /data/arquivos/ · /data/audios/                   │
│  Arquivos originais preservados, conteúdo gerado adicional  │
└─────────────────────────────────────────────────────────────┘
```

---

## Mapa de Arquivos

```
Professor.ia/
│
├── web/                              CAMADA 3 — Frontend
│   ├── index.html
│   ├── app.js
│   └── style.css
│
├── backend/                          CAMADA 2 — Gerador
│   │
│   ├── app.py                        Entry point FastAPI (CORS, routers)
│   │
│   ├── SrEdmundo/                    Camada de API
│   │   ├── rotas.py                    /gerar/* — modo avulso (legado)
│   │   ├── rotas_repositorio.py        /repositorio/* — modo principal
│   │   └── orquestrador.py             Pipeline central
│   │
│   ├── skills/
│   │   ├── motor.py                  ★ Camada transversal
│   │   │                               Lê base_conhecimento e injeta em tudo
│   │   │                               chamar() · chamar_json()
│   │   │
│   │   ├── entrada/
│   │   │   └── SK_HarryPotter.py       Extrai texto de qualquer formato
│   │   │                               PDF · DOCX · PPTX · XLSX · HTML
│   │   │                               TXT · MD · JSON · XML · áudio · vídeo
│   │   │
│   │   ├── processamento/            Todas usam o motor.py
│   │   │   ├── skill_bigdani.py        Aprender — análise pedagógica
│   │   │   ├── skill_elaborar.py       Elaborar — plano didático ★ novo
│   │   │   ├── skill_resumo.py         Resumir — 3 níveis
│   │   │   ├── skill_quiz.py           Quiz — múltipla escolha + abertas
│   │   │   ├── skill_glossario.py      Glossário — termos-chave
│   │   │   ├── skill_exercicios.py     Exercícios práticos aplicados
│   │   │   └── skill_revisar.py        Corretor — refina qualquer saída
│   │   │
│   │   └── saida/
│   │       ├── skill_slides.py         Resumo → HTML Reveal.js (sem API)
│   │       ├── skill_narrador.py       Texto → MP3 (OpenAI TTS)
│   │       └── skill_video.py          Resumo → HTML + narração embutida
│   │
│   ├── base_conhecimento/            ★ Cérebro transversal
│   │   ├── CONTEXTO.md                 Quem somos, objetivo, princípios
│   │   ├── PEDAGOGIA.md                Como ensinamos
│   │   ├── IDENTIDADE.md               Visual (cores, layout) + verbal (tom)
│   │   ├── APRESENTACAO.md             Estrutura de cada formato de saída
│   │   └── banco.py                    SQLite: CRUD áreas, arquivos, conteúdo
│   │
│   ├── modelos/
│   │   └── tipos.py                  Pydantic: CustoSkill, Area, Arquivo...
│   │
│   └── data/                         CAMADA 1 — Runtime
│       ├── professor.db                SQLite database
│       ├── arquivos/{area_id}/         Originais preservados
│       └── audios/                     MP3 gerados
│
└── docs/
    └── arquitetura.md                Este documento
```

---

## Pipeline Completo

```
ARQUIVO ENTRA (qualquer formato)
        │
        ▼
┌───────────────┐
│ SK_HarryPotter│  Extrai texto bruto
│  (entrada)    │  15+ formatos suportados
└──────┬────────┘
       │ texto bruto
       ▼
┌───────────────┐
│ skill_bigdani │  APRENDER                   ← motor.chamar_json()
│               │  Entende o conteúdo:
│               │  tema, conceitos, nível,
│               │  público, pré-requisitos
└──────┬────────┘
       │ conhecimento estruturado (JSON)
       ▼
┌───────────────┐
│ skill_elaborar│  ELABORAR ★ novo            ← motor.chamar_json()
│               │  Plano didático:
│               │  ângulo de entrada,
│               │  narrativa central,
│               │  sequência de ensino,
│               │  pontos críticos,
│               │  armadilhas comuns,
│               │  formatos recomendados
└──────┬────────┘
       │ plano didático (JSON)
       ▼
┌──────────────────────────────────────────────────┐
│              SKILLS DE PROCESSAMENTO              │
│                                                   │
│  skill_resumo ──────────────────────→ markdown   │ ← motor.chamar()
│  skill_quiz ────────────────────────→ JSON       │ ← motor.chamar_json()
│  skill_glossario ───────────────────→ JSON       │ ← motor.chamar_json()
│  skill_exercicios ──────────────────→ JSON       │ ← motor.chamar_json()
│                                                   │
│  Todas recebem o plano do Elaborar                │
│  e seguem a estratégia didática                   │
└──────────────┬────────────────────────────────────┘
               │ (opcional)
               ▼
        ┌──────────────┐
        │ skill_revisar│  Refina qualquer saída  ← motor.chamar() / chamar_json()
        │  (corretor)  │  Sem mudar o formato
        └──────┬───────┘
               │
               ▼
┌──────────────────────────────────────────────────┐
│              SKILLS DE SAÍDA                      │
│                                                   │
│  skill_slides ──── resumo ──→ HTML Reveal.js      │  sem chamada API
│  skill_narrador ── resumo ──→ MP3                 │  OpenAI TTS
│  skill_video ───── resumo ──→ HTML + áudio        │  Claude + TTS
└──────────────────────────────────────────────────┘
               │
               ▼
        BANCO DE DADOS
  conteudo_gerado (arquivo_id, tipo, conteudo, custo_brl)
```

---

## Motor — Camada Transversal

O motor é o que conecta tudo. Toda skill que chama o Claude passa por ele.

```
skill define:    system com sua instrução específica
motor injeta:    CONTEXTO.md + PEDAGOGIA.md + IDENTIDADE.md + APRESENTACAO.md + system da skill

Claude recebe:   base de conhecimento completa + instrução da skill
```

```python
# O que uma skill faz hoje (2 linhas):
from skills.motor import chamar_json

dados, tk_in, tk_out = chamar_json(system="...", prompt=_PROMPT.format(...))
```

---

## Orquestrador

Dado um arquivo e um objetivo, resolve dependências e executa o pipeline.

### Pipelines disponíveis

| Objetivo | Etapas executadas |
|----------|-------------------|
| `aprender` | extrair → aprender → elaborar |
| `resumo` | extrair → aprender → elaborar → resumo |
| `quiz` | extrair → aprender → elaborar → quiz |
| `glossario` | extrair → glossario |
| `exercicios` | extrair → aprender → elaborar → exercicios |
| `slides` | extrair → aprender → elaborar → resumo → slides |
| `narracao` | extrair → aprender → elaborar → resumo → narracao |
| `video` | extrair → aprender → elaborar → resumo → video |
| `tudo` | extrair → aprender → elaborar → resumo → quiz → glossario → exercicios → slides → narracao |

### Reuso automático

Se uma etapa já foi gerada para aquele arquivo, o orquestrador reusa sem refazer.

```python
# Primeira vez: roda tudo
orquestrador.executar(42, "tudo")
# → etapas_executadas: ["extrair", "aprender", "elaborar", "resumo", "quiz", ...]

# Segunda vez: roda só o que mudou
orquestrador.executar(42, "video")
# → etapas_executadas: ["video"]
# → etapas_reusadas:   ["aprender", "elaborar", "resumo"]
```

---

## API — Endpoints

### `/gerar/*` — Modo avulso (legado)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/gerar/resumo` | Texto → resumo |
| POST | `/gerar/resumo/pdf` | PDF → resumo |
| POST | `/gerar/quiz` | Texto → quiz |
| POST | `/gerar/slides/do-resumo/{id}` | Resumo salvo → slides |
| POST | `/gerar/video/do-resumo/{id}` | Resumo salvo → vídeo |

### `/repositorio/*` — Modo principal

**Áreas e arquivos:**

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/repositorio/areas` | Criar área |
| GET | `/repositorio/areas` | Listar áreas |
| POST | `/repositorio/areas/{id}/arquivos` | Upload arquivo |
| GET | `/repositorio/areas/{id}/arquivos` | Listar arquivos da área |
| DELETE | `/repositorio/arquivos/{id}` | Deletar arquivo |
| PUT | `/repositorio/arquivos/{id}` | Substituir arquivo |
| GET | `/repositorio/arquivos/recentes` | Arquivos com conteúdo gerado |
| GET | `/repositorio/arquivos/{id}/conteudo` | Listar conteúdo gerado |

**Geração via orquestrador:**

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/repositorio/arquivos/{id}/aprender` | Aprender + Elaborar |
| POST | `/repositorio/arquivos/{id}/gerar/resumo` | Gerar resumo |
| POST | `/repositorio/arquivos/{id}/gerar/quiz` | Gerar quiz |
| POST | `/repositorio/arquivos/{id}/gerar/glossario` | Gerar glossário |
| POST | `/repositorio/arquivos/{id}/gerar/exercicios` | Gerar exercícios |
| POST | `/repositorio/arquivos/{id}/gerar/slides` | Gerar slides |
| POST | `/repositorio/arquivos/{id}/gerar/narracao` | Gerar narração (MP3) |
| POST | `/repositorio/arquivos/{id}/gerar/video` | Gerar vídeo narrado |
| POST | `/repositorio/arquivos/{id}/gerar/tudo` | Gerar tudo em sequência ★ |
| GET | `/repositorio/arquivos/{id}/narracao` | Servir MP3 |
| GET | `/repositorio/arquivos/{id}/video` | Servir HTML do vídeo |

---

## Skills — Status

| Skill | Tipo | Usa Motor | Status |
|-------|------|-----------|--------|
| SK_HarryPotter | entrada | Não (sem Claude) | ✅ Completo |
| skill_bigdani | processamento | ✅ | ✅ Completo |
| skill_elaborar | processamento | ✅ | ✅ Novo |
| skill_resumo | processamento | ✅ | ✅ Completo |
| skill_quiz | processamento | ✅ | ✅ Completo |
| skill_glossario | processamento | ✅ | ✅ Completo |
| skill_exercicios | processamento | ✅ | ✅ Completo |
| skill_revisar | processamento | ✅ | ✅ Completo |
| skill_slides | saída | Não (parsing local) | ✅ Completo |
| skill_narrador | saída | Não (OpenAI TTS) | ✅ Completo |
| skill_video | saída | Parcial (roteiros) | ✅ Completo |

---

## Base de Conhecimento

Injetada pelo motor em toda chamada ao Claude.

| Arquivo | Conteúdo |
|---------|----------|
| `CONTEXTO.md` | Quem somos, problema, solução, princípios, fases |
| `PEDAGOGIA.md` | Como ensinamos: progressão, andragogia, carga cognitiva |
| `IDENTIDADE.md` | Visual (cores, layout, marca) + verbal (tom, voz, audiências) |
| `APRESENTACAO.md` | Estrutura de cada formato: resumo, quiz, slides, exercícios |

---

## Banco de Dados

SQLite em `data/professor.db`.

```
areas
  id · nome · descricao · criado_em

arquivos
  id · area_id → areas · nome_original · tipo · caminho · tamanho_mb · enviado_por · criado_em

conteudo_gerado
  id · arquivo_id → arquivos · tipo · conteudo · custo_brl · criado_em
  tipos: aprender | elaborar | resumo | quiz | glossario | exercicios
         slides | narracao | video

resumos  (compatibilidade com rotas legado)
  id · resumo · nivel · criado_em
```

---

## Visão de Custos

### Processamento Claude Sonnet 4.6

| Operação | Tokens estimados | Custo aprox. (BRL) |
|----------|-----------------|---------------------|
| Aprender | ~15k tokens | R$ 0,25 – R$ 0,80 |
| Elaborar | ~10k tokens | R$ 0,15 – R$ 0,50 |
| Resumo | ~40k tokens | R$ 0,60 – R$ 2,00 |
| Quiz | ~10k tokens | R$ 0,15 – R$ 0,50 |
| Glossário | ~8k tokens | R$ 0,10 – R$ 0,40 |
| Exercícios | ~12k tokens | R$ 0,20 – R$ 0,60 |
| **Pipeline completo** | ~95k tokens | **R$ 1,45 – R$ 4,80** |

> Referência: Claude Sonnet 4.6 — US$ 3/M tokens input, US$ 15/M tokens output. Câmbio ~R$ 5,80.

### Narração (OpenAI TTS)

| Serviço | Custo | Observação |
|---------|-------|------------|
| OpenAI TTS (tts-1) | ~US$ 0,015/1k chars | Voz "nova", qualidade ok |

### Transcrição (Whisper)

| Serviço | Custo | Observação |
|---------|-------|------------|
| OpenAI Whisper API | ~US$ 0,36/hora | Para áudio/vídeo |

---

## Próximos Passos

| # | O que | Por quê |
|---|-------|---------|
| 1 | Migrar `skill_video` para usar motor | Única skill que ainda chama Claude direto |
| 2 | Extrator de URL no SK_HarryPotter | Ampliar fontes de entrada |
| 3 | Autenticação básica | Necessário para Fase 2 (uso interno) |
| 4 | Trilhas de formação | LMS — Fase 2 |
| 5 | Avatar (HeyGen / D-ID) | Fase futura |
