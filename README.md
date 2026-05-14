# linkedin-content-agent

Agente local que analisa as minhas postagens recentes no LinkedIn, identifica
o que funciona, e propoe novos posts no meu estilo (sem postar automatico,
porque LinkedIn bane).

> Repo separado do `buscarv` (dashboard de vagas). Reusa o pattern de Playwright
> com sessao persistente, mas a logica de conteudo e propria.

---

## Por que existir

Hoje, gerar post no LinkedIn com LLM cai em dois extremos:
- **Prompt unico**: "escreva um post sobre X". Sai generico, parecido com mais
  10 mil posts saturados ("Perdi 3 horas fazendo X...").
- **Manual total**: voce escreve do zero toda vez, e nao tem visibilidade do
  que ja performou ou nao.

Esse agente fica no meio:
1. Le os seus posts antigos (raspagem autenticada do seu proprio perfil).
2. Persiste em SQLite com metricas (reactions, comments, shares).
3. Quando voce pede um draft, ele monta few-shot com **os seus** melhores
   posts e gera variacoes no seu estilo.
4. Bate os drafts contra uma lista de anti-padroes (hooks saturados, jargao,
   etc) antes de mostrar.

---

## Estado atual (Phase 0 — bootstrap)

| Componente | Status | Onde |
| --- | --- | --- |
| Estrutura de repo | OK | `app/`, `scripts/`, `templates/`, `tests/` |
| Login persistente Playwright | OK (copiado do buscarv) | `scripts/setup_session.py` |
| Schema SQLite (posts, metrics, drafts, briefings) | OK | `app/db/schema.sql` |
| Repo gateway com CRUD basico | OK | `app/repo.py` |
| Smoke tests | OK | `tests/test_repo_smoke.py` |
| Agente Claude Code | OK (skill v0) | `.claude/agents/linkedin-content-manager.md` |
| Scraper de atividade recente | **TODO** (esqueleto pronto) | `scripts/scrape_my_activity.py` |
| Geracao de drafts (Claude API) | **TODO** | `scripts/generate_drafts.py` |
| Imagens / carrossel | **TODO** | `scripts/gen_image.py`, `scripts/gen_carousel.py` |
| UI Streamlit | **TODO** | `app/streamlit_app.py` |
| Agendamento (lembrete) | **TODO** | cron / GitHub Actions |

---

## O que veio do buscarv

Reaproveitado e adaptado pro contexto deste repo:

| Vindo de | Adaptado em | Razao |
| --- | --- | --- |
| `buscarv/scripts/setup_sessions.py` | `scripts/setup_session.py` | Mesmo padrao de `launch_persistent_context`, profile dir local |
| `buscarv/scripts/scrape_linkedin.py` | `scripts/scrape_my_activity.py` | Circuit breaker, mojibake fixer, save-as-you-go |
| `buscarv/app/repo.py` | `app/repo.py` | Single-gateway pattern, validacao de status, JSON cols |
| `buscarv/.gitignore` | `.gitignore` | Cobre sessoes, secrets, sqlite, screenshots |

> Nao trouxe: ATS adapters, scoring por fit de curriculo, Turso libSQL,
> Streamlit pages do funil de vagas. Sao especificos do buscarv.

---

## Stack

- **Python 3.13+**
- **Playwright** (sync) com `launch_persistent_context` pra reusar login
- **SQLite** local (`data/linkedin.sqlite3`); migrar pra Turso/Postgres so se
  virar deploy multi-user
- **Anthropic SDK** (Claude) pra geracao de drafts; com prompt caching pra
  reduzir custo do few-shot dos seus posts antigos
- **Pillow** pra imagens simples; **fal.ai** pra capas (opcional)
- **pytest** + **ruff** + **black**

---

## Setup

```bash
# 1) Clone
git clone https://github.com/MatheusZacche/linkedin-content-agent.git
cd linkedin-content-agent

# 2) Venv + deps
python -m venv .venv
.venv\Scripts\activate         # Windows
# source .venv/bin/activate    # Linux/Mac
pip install -r requirements.txt
playwright install chromium

# 3) Secrets
copy .env.example .env         # ou: cp .env.example .env
# preencha ANTHROPIC_API_KEY e LINKEDIN_PROFILE_SLUG

# 4) Banco local
python scripts/init_db.py

# 5) Login no LinkedIn (abre janela do browser)
python scripts/setup_session.py

# 6) Raspar atividade recente (ainda esqueleto; selectors faltando)
python scripts/scrape_my_activity.py --profile-slug matheuszacche --max-scrolls 5

# 7) Rodar testes
pytest -q
```

---

## Roadmap

### Phase 1 — Coleta funcional

- [ ] Preencher `_extract_posts` em `scripts/scrape_my_activity.py` com selectors
      validos do `/recent-activity/all/`
- [ ] Capturar comentarios por post (`/feed/update/<urn>/?...`)
- [ ] Capturar metricas de cada post (reactions, comments, shares,
      impressoes quando visiveis pro dono)
- [ ] Loader que pega o JSON do scrape e popula `posts` + `post_metrics`
- [ ] Detector de mudanca: se ja existe, so cria novo snapshot em `post_metrics`

### Phase 2 — Geracao de drafts

- [ ] `scripts/generate_drafts.py` lendo briefing de `templates/post_brief.md`
- [ ] Few-shot com top-K dos seus posts (rankeados por engagement_rate)
- [ ] **Prompt caching** dos seus posts antigos (eles nao mudam entre
      chamadas; e o que cachear)
- [ ] Filtro post-geracao: descartar draft que casa anti-padrao
- [ ] Salvar 3-5 variacoes em `drafts/<data>-<slug>.md` com frontmatter

### Phase 3 — Analise

- [ ] CLI `python -m app.analytics weekly` mostrando:
  - Melhores horarios pra mim, especificamente
  - Hooks que performaram (agrupado por hook_pattern)
  - Temas que comentaram mais
- [ ] Comparar com bench: ler N posts de gente que eu admiro
  (data analysts BR) e detectar padroes deles vs meus

### Phase 4 — Imagens / carrossel

- [ ] `scripts/gen_image.py` chamando fal.ai (Nano Banana) com prompt do post
- [ ] `scripts/gen_carousel.py` montando PDF de N slides via Pillow
- [ ] Templates de estilo visual (cor, fonte) parametrizaveis

### Phase 5 — UX

- [ ] Streamlit app: ver pipeline de drafts, marcar approved/published,
      visualizar metricas
- [ ] Comando `/loop` ou cron: scrape semanal automatico
- [ ] **NAO** automatizar publicacao. Risco de ban + perda de voz autoral

---

## Plugins / skills Claude Code recomendados

Sao addons que ja existem no harness e ajudam aqui (instalar via `/plugin` ou
configurar `~/.claude/settings.json`):

| Skill | Pra que | Como usar |
| --- | --- | --- |
| `claude-api` | Construir o cliente Claude com prompt caching e tool use | Quando for escrever `scripts/generate_drafts.py` |
| `python-patterns` / `python-testing` | Patterns idiomaticos, pytest, fixtures | Default em tudo |
| `playwright` MCP | Inspecionar DOM do LinkedIn pra achar selectors atuais | Antes de preencher `_extract_posts` |
| `fal-ai-media` | Imagem e video via fal.ai | Phase 4 (capas e carrossel) |
| `content-engine` | Geracao de conteudo nativo por plataforma | Inspiracao pra prompts de Phase 2 |
| `exa-search` ou `deep-research` | Pesquisar tendencias de tema antes de escrever | Quando travar em ideia |
| `crosspost` | Distribuir o mesmo conteudo em X / Bluesky / Threads | Phase 5+ (se quiser expandir) |
| `e2e-testing` | Testes Playwright do scrape | Phase 1 fim |

E o **proprio agente** deste repo (em `.claude/agents/linkedin-content-manager.md`):
invoque com `@linkedin-content-manager` ou via Skill.

---

## Esquema do banco

`app/db/schema.sql`. Tabelas:

- `posts` — um por post publicado. PK e o `urn:li:activity:...`
- `post_metrics` — historico de metricas. PK composta (post_id, captured_at)
  permite varios snapshots por post pra ver crescimento
- `comments_received` — comentarios que voce recebeu (audiencia revela tema)
- `drafts` — texto gerado pelo agente, com status (generated/approved/...)
- `briefings` + `draft_briefings` — entrada que originou cada draft
- `themes` — vocabulario controlado de temas

---

## Anti-padroes (resumo)

Lista cheia em `templates/anti_patterns.md`. Resumo do que **nao** pode sair
do agente:

- Hooks: "Perdi N horas", "Ninguem te conta isso", "X coisas que aprendi"
- Final em pergunta vaga ("o que voces acham?")
- Vocabulario saturado: "game changer", "muda tudo", "mindset", "jornada"
- Lista numerada de dicas genericas
- Emoji em cada paragrafo
- Em PT-BR, sem travessao (usar dois pontos ou parenteses)

---

## Avisos

- **Scraping autenticado tem risco**: LinkedIn pode rate-limit ou flagear.
  Use moderado (1-2 runs por semana), sempre com user agent normal, e
  intervalos randomicos.
- **Nao publicar automatico**: o agente sugere; voce posta. Manter a voz
  autoral e evitar acionar antifraud da plataforma.
- **PII**: o `.browser_profile/` contem cookies de sessao. Nunca commitar.
  O `data/*.sqlite3` contem seus posts. Tambem fica fora do git.

---

## Estrutura final

```
linkedin-content-agent/
├── .claude/
│   └── agents/
│       └── linkedin-content-manager.md  # skill Claude Code
├── .env.example
├── .gitignore
├── CLAUDE.md                            # project instructions p/ Claude Code
├── README.md
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── db/
│   │   ├── __init__.py
│   │   └── schema.sql
│   ├── repo.py
│   └── scrapers/
│       └── __init__.py
├── scripts/
│   ├── init_db.py
│   ├── scrape_my_activity.py
│   └── setup_session.py
├── templates/
│   ├── anti_patterns.md
│   └── post_brief.md
└── tests/
    ├── __init__.py
    └── test_repo_smoke.py
```

---

## Licenca

Privado / pessoal por enquanto. Decidir depois.
