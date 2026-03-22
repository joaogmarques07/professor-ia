# Contexto e Objetivo do Projeto — Professor.ia

> Este documento é a diretriz central do projeto.
> Toda decisão de arquitetura, skill, interface ou custo deve ser avaliada à luz deste contexto.

---

## O Problema

Uma empresa com múltiplos setores enfrenta dois desafios críticos e interligados:

**1. Conhecimento fragmentado**
O conhecimento institucional está espalhado em diferentes SharePoints por área. Não há uma visão consolidada, não há padrão de organização e não há forma eficiente de o time comercial (ou qualquer colaborador) acessar o que precisa, quando precisa.

**2. Treinamento caro e lento**
Transformar esse conhecimento em conteúdo de treinamento — cursos, onboardings, vídeos — é um processo manual, demorado e frágil. Quando a informação muda (e muda sempre), todo o material precisa ser refeito. Pessoas gastam horas montando apresentações, gravando vídeos e estruturando cursos que logo ficam desatualizados.

---

## A Solução — Professor.ia

Uma plataforma inteligente que recebe qualquer conteúdo, aprende com ele e o transforma automaticamente em material educacional pronto para uso — em múltiplos formatos.

### As três camadas da plataforma

```
┌─────────────────────────────────────────────────────┐
│  CAMADA 1 — REPOSITÓRIO                             │
│  Armazena e organiza os arquivos originais          │
│  (como SharePoint, mas inteligente)                 │
├─────────────────────────────────────────────────────┤
│  CAMADA 2 — GERADOR                                 │
│  IA aprende com os arquivos e gera conteúdo         │
│  educacional em múltiplos formatos                  │
├─────────────────────────────────────────────────────┤
│  CAMADA 3 — PLATAFORMA DE APRENDIZADO               │
│  Exibe o conteúdo gerado, organizado em trilhas     │
│  de formação, com navegação, vídeos e progresso     │
└─────────────────────────────────────────────────────┘
```

---

### Pilares

**Repositório inteligente**
Centraliza o conhecimento de todas as áreas em um único lugar, organizado, padronizado e pesquisável. Substitui o modelo de SharePoints isolados. Cada área contribui com seu conteúdo; a plataforma garante que ele esteja acessível e estruturado para quem precisa.

A plataforma **mantém os arquivos originais** e aceita novos a qualquer momento. Funciona como um SharePoint, mas com inteligência: organizado por área, com controle de quem acessa o quê, e com a capacidade de gerar conteúdo educacional a partir de qualquer documento armazenado.

Características do repositório:
- **Organizado por área** — cada setor tem seu espaço, com visibilidade controlada
- **Arquivos preservados** — o original nunca é perdido; o que a IA gera é adicional
- **Sempre aberto a novos conteúdos** — qualquer colaborador autorizado pode subir arquivos a qualquer momento
- **Pesquisável** — o usuário pode buscar por tema, área ou tipo de conteúdo
- **Vivo** — quando um arquivo é atualizado, o material gerado pode ser regenerado com um clique, sem retrabalho manual

**Professor automatizado**
A partir do conteúdo ingerido, a plataforma gera automaticamente:
- Resumos por nível (básico, intermediário, avançado)
- Apresentações (slides, fluxogramas)
- Vídeos narrados
- Exercícios e avaliações
- Avatar virtual como "professor" (fase futura)

**Plataforma de aprendizado (LMS)**
O usuário final não vê arquivos brutos — ele navega por uma plataforma organizada, com:
- **Pastas e áreas** — estrutura lógica por setor/tema, não por tipo de arquivo
- **Trilhas de formação** — sequências de conteúdo curadas por assunto (ex: "Onboarding Comercial", "Produto X — Certificação")
- **Vídeos integrados** — gerados pela IA ou enviados manualmente, disponíveis dentro das trilhas
- **Navegação entre conteúdos** — o usuário transita entre resumo, slides, vídeo e exercícios do mesmo tema
- **Progresso** — a plataforma sabe o que cada pessoa já viu e onde parou

**Aprendizado de verdade**
O conteúdo não é só resumido — ele passa por uma camada pedagógica que avalia a melhor forma de apresentá-lo para que seja compreendido, retido e aplicado. A plataforma "vende" o conhecimento para quem aprende.

---

## Fluxo Central

```
ENTRADA
  Arquivo (PDF, DOCX, PPTX, áudio, vídeo, planilha...)
    ↓
SK_HarryPotter (Receptor)
  Extrai texto bruto + preserva arquivo original no repositório
    ↓
Skill: Aprender
  Entende o conteúdo, identifica tema, área e estrutura do conhecimento
    ↓
Skill: Elaborar
  Aplica lógica pedagógica — como ensinar isso da melhor forma
    ↓
Orquestrador
  Decide e dispara as skills de saída necessárias
    ↓
Skills de Saída:
  • Resumo (por nível)
  • Slides / Fluxograma
  • Vídeo narrado (TTS + imagens)
  • Exercícios e avaliações
  • Avatar professor (futuro)
    ↓
PLATAFORMA — onde o usuário final consome
  • Navega por área / pasta
  • Acessa a trilha de formação do tema
  • Assiste ao vídeo, lê o resumo, faz os exercícios
  • Progresso registrado
```

---

## Perfis de usuário

| Perfil | Quem é | O que faz |
|--------|--------|-----------|
| **Editor** | Dono do conteúdo, gestor de área | Sobe arquivos, organiza pastas, dispara geração de conteúdo, gerencia o que está publicado |
| **Usuário** | Colaborador, time comercial, aluno | Consome o conteúdo — navega pela plataforma, assiste vídeos, faz exercícios, acompanha trilhas |

> Trilhas de formação e armazenamento de vídeo serão definidos em fase posterior — o objetivo já está registrado.

---

## Público-alvo e Escopo

| Fase | Público | Objetivo |
|------|---------|----------|
| **1 — Agora** | Desenvolvedor (você) | Validar o conceito, testar o pipeline completo |
| **2 — Médio prazo** | Empresa interna | Resolver o problema real de conhecimento e treinamento |
| **3 — Longo prazo** | Mercado B2B/B2C | Produto escalável e vendável para outras empresas |

A solução deve ser **genérica desde o início** — não amarrada à empresa específica, para que possa ser adaptada a qualquer cliente.

---

## Princípios que guiam cada decisão

1. **Custo sempre visível** — toda operação que consome API deve informar o custo estimado ao usuário.
2. **Simples primeiro** — construir o mínimo que funciona, depois escalar.
3. **Repositório + inteligência** — a plataforma armazena os arquivos originais (como um SharePoint) E aprende com eles para gerar conteúdo educacional. Os dois andam juntos.
4. **Atualização sem retrabalho** — quando o conteúdo-fonte muda, o material gerado pode ser regerado com um clique.
5. **Multi-formato** — o mesmo conhecimento deve poder ser entregue de formas diferentes para perfis diferentes.
6. **Aprendizado, não apenas informação** — a saída deve ser pedagógica, não só um resumo do que entrou.

---

## O que NÃO é o Professor.ia

- Não é só um buscador de documentos — é um repositório que também ensina
- Não é um chatbot de perguntas e respostas (pelo menos não na fase atual)
- Não é uma ferramenta só de resumo — resumo é uma das saídas, não o produto
- Não substitui o arquivo original — ele é sempre preservado

---

*Última revisão: 2026-03-22 — adicionado: três camadas (repositório + gerador + LMS), trilhas de formação, navegação por área/pasta, vídeos integrados, progresso do usuário*
