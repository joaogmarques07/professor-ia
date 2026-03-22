# /dev-setup — Setup do ambiente de desenvolvimento

Guie o usuário pelo setup completo do projeto, passo a passo.
Confirme cada etapa antes de avançar para a próxima.

## Pré-requisitos

Verifique se o usuário tem:
- Python 3.11 ou superior (`python --version`)
- Git (`git --version`)

## Passo 1 — Clonar o repositório (se ainda não tiver)

```bash
git clone <url-do-repositorio>
cd professor-ia
```

## Passo 2 — Criar e ativar o ambiente virtual

```bash
cd backend
python -m venv .venv

# Linux/Mac:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate
```

Confirme que o prompt mudou para `(.venv)` antes de continuar.

## Passo 3 — Instalar dependências

```bash
pip install -r requirements.txt
```

Se der erro em algum pacote, informe o erro exato e sugira solução.

## Passo 4 — Configurar variáveis de ambiente

```bash
cp .env.example .env
```

Abra o arquivo `.env` e peça ao usuário para preencher:
- `ANTHROPIC_API_KEY` — obrigatória para geração de conteúdo
- `OPENAI_API_KEY` — necessária apenas para transcrição de áudio/vídeo

Onde conseguir as chaves:
- Anthropic: https://console.anthropic.com
- OpenAI: https://platform.openai.com/api-keys

## Passo 5 — Subir a API

```bash
uvicorn app:app --reload
```

A API sobe em `http://localhost:8000`.
O banco SQLite (`backend/data/professor.db`) é criado automaticamente.

## Passo 6 — Confirmar que está funcionando

Teste o health check:
```bash
curl http://localhost:8000/health
# esperado: {"status": "ok", "versao": "0.1.0"}
```

Acesse a documentação interativa: `http://localhost:8000/docs`

## Passo 7 — Teste de ponta a ponta (opcional)

Guie o usuário pelo fluxo completo usando o `/docs` do FastAPI:

1. `POST /repositorio/areas` — criar área (ex: `{"nome": "Teste", "descricao": "Área de teste"}`)
2. `POST /repositorio/areas/{id}/arquivos` — subir um PDF ou DOCX qualquer
3. `POST /pipeline/arquivos/{id}/processar` — processar com `{"skills": ["resumo", "slides"]}`
4. Ver o resultado com resumo, slides e custo em BRL

## Se algo der errado

| Problema | Solução |
|----------|---------|
| `ModuleNotFoundError` | Confirmar que o venv está ativado e rodar `pip install -r requirements.txt` novamente |
| `ANTHROPIC_API_KEY not found` | Verificar se o arquivo `.env` existe em `backend/` e tem a chave preenchida |
| Porta 8000 em uso | Usar `uvicorn app:app --reload --port 8001` |
| Erro ao subir a API | Compartilhar o traceback completo para diagnóstico |
