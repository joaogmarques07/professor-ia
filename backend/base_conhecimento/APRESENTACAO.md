# Apresentação — Como Formatar Cada Saída

> Define a estrutura esperada de cada formato gerado pelo Professor.ia.
> Toda skill deve seguir estes padrões ao gerar conteúdo.

---

## Resumo (Markdown)

Estrutura obrigatória para todos os níveis:

```
# [Título do tema]

## Visão geral
2-3 frases que respondem: o que é, por que existe, para que serve.

## [Conceito ou seção principal]
Explicação + exemplo ou aplicação.
Use listas quando houver enumeração real — não force bullet points.

## Pontos de atenção
O que costuma gerar dúvida, erro ou confusão.
Máx. 4-5 itens.

## Como aplicar
Situação concreta onde esse conhecimento entra em ação.
```

Regras:
- Títulos com `##`, subtítulos com `###`
- Listas com `-` para itens sem ordem; numeradas (`1.`) quando há sequência
- Negrito `**termo**` para conceitos importantes — use com moderação
- Máx. 5 itens por lista; agrupe se houver mais
- Sem tabelas a menos que haja comparação real a fazer

---

## Quiz (JSON)

```json
{
  "titulo": "nome do tema avaliado",
  "multipla_escolha": [
    {
      "pergunta": "pergunta direta, sem ambiguidade",
      "opcoes": ["A) texto", "B) texto", "C) texto", "D) texto"],
      "resposta_correta": "A",
      "explicacao": "por que esta é correta — e por que as outras não são"
    }
  ],
  "abertas": [
    {
      "pergunta": "pergunta que exige raciocínio, não memorização",
      "resposta_esperada": "o que uma boa resposta deve conter"
    }
  ]
}
```

Regras:
- Perguntas testam compreensão, não decoreba
- Distratores (opções erradas) devem ser plausíveis, não obviamente errados
- Explicação deve ensinar, não apenas confirmar a resposta
- Perguntas abertas devem exigir síntese ou aplicação

---

## Glossário (JSON)

```json
{
  "glossario": [
    {
      "termo": "nome do conceito",
      "definicao": "definição clara, sem jargão desnecessário",
      "exemplo": "exemplo de uso real ou aplicação prática"
    }
  ]
}
```

Regras:
- Entre 8 e 20 termos — priorizar os mais relevantes e específicos do tema
- Definição em 1-2 frases; sem copiar do dicionário
- Exemplo deve ser concreto, não genérico
- Ordenar alfabeticamente

---

## Exercícios (JSON)

```json
{
  "exercicios": [
    {
      "titulo": "nome curto e descritivo",
      "contexto": "situação real onde o conhecimento é aplicado",
      "tarefa": "o que o aluno deve fazer — ação clara e mensurável",
      "criterios": ["como saber se fez bem — critério 1", "critério 2"],
      "nivel": "basico | intermediario | avancado"
    }
  ]
}
```

Regras:
- Exercícios são práticos — o aluno faz algo, não apenas responde
- Contexto deve ser situacional, não abstrato
- Tarefa deve ser clara o suficiente para o aluno começar sem dúvidas
- Critérios devem ser observáveis, não subjetivos

---

## Slides (HTML — Reveal.js)

Estrutura de cada slide:
- **Capa:** título do tema + marca Professor.ia
- **Slides de conteúdo:** 1 ideia principal por slide, máx. 5 pontos por slide
- Sem parágrafos — apenas frases curtas e pontos-chave
- Título do slide = a ideia central daquele bloco

Regras de conteúdo:
- Máx. 6-8 slides por apresentação
- Primeiro slide após capa = visão geral
- Último slide = como aplicar ou próximos passos
- Sem bullet points genéricos — cada ponto deve ter peso real

---

## Narração (texto para TTS)

- Frases com máx. 20 palavras
- Sem markdown — texto puro, corrido
- 2-4 frases por slide (quando narrar apresentação)
- Começa sempre pelo contexto, não pela definição
- Finaliza com aplicação ou próxima ideia, não com "e assim vemos que..."
