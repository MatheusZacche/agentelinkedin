# linkedin-content-agent — Project Instructions

Agente que analisa minhas postagens recentes no LinkedIn, identifica padroes de
performance, e sugere novos posts no meu estilo. Repo separado do `buscarv`,
mas reusa pattern de Playwright + sessao persistente.

## Stack

- Python 3.13+
- Playwright (sync API) com persistent context pra scraping autenticado
- SQLite local (`data/linkedin.sqlite3`)
- Claude API (Anthropic SDK) pra geracao de drafts
- Opcional: fal.ai pra imagens/capas; Streamlit pra UI

## Diretorios

- `scripts/` — entrypoints CLI (setup, scrape, init_db, geradores)
- `app/` — codigo de aplicacao (repo, scrapers, scoring)
  - `app/db/schema.sql` — fonte unica do schema
  - `app/repo.py` — gateway SQLite
  - `app/scrapers/` — adapters de raspagem (LinkedIn por enquanto)
- `templates/` — briefings de post, lista de anti-padroes
- `tests/` — pytest (smoke + unit)
- `.claude/agents/linkedin-content-manager.md` — agente Claude Code
- `.browser_profile/` — gitignored; sessao do Chromium logada

## Workflow basico

1. `python scripts/setup_session.py` — logar no LinkedIn (1x)
2. `python scripts/init_db.py` — criar DB local
3. `python scripts/scrape_my_activity.py --profile-slug <voce>` — puxar posts
4. (futuro) `/linkedin-content-manager` no Claude Code — gerar drafts a partir
   do historico + briefing

## Regras de estilo dos posts

Ver `templates/anti_patterns.md`. Resumo:
- Primeira pessoa, especifica, numeros reais
- Sem hooks saturados ("perdi X horas", "ninguem te conta")
- Sem pergunta final generica
- Sem travessao na escrita PT-BR

## Secrets

- `.env` na raiz (gitignored). Template em `.env.example`.
- Chave Claude API: `ANTHROPIC_API_KEY`
- Nunca commitar cookies do `.browser_profile/`
