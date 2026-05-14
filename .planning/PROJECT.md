# linkedin-content-agent

## What This Is

Agente que age como **social media manager senior** da marca pessoal do
Matheus no LinkedIn. NAO e um gerador de texto. Ele:

1. **Diagnostica** a situacao (que dia/hora e, o que voce postou recentemente,
   gap por pilar de conteudo, performance do que ja foi publicado).
2. **Decide** se vale postar AGORA — e tem permissao de recusar. Se a janela
   ja fechou, se voce postou ontem, se o tema repete demais, ele diz isso.
3. **Planeja** angulo, formato e framework antes de qualquer texto.
4. **Gera** N variacoes ancoradas em few-shot dos seus posts top (engagement
   real) — nao em template generico.
5. **Critica o proprio output** com rubrica multi-dimensional (voice match,
   hook strength, especificidade, anti-padroes, predicao de engagement).
   Itera ate passar threshold OU desiste e pede ajuda humana.
6. **Aprende** comparando engagement previsto vs real apos a publicacao.

NAO publica automaticamente. NUNCA. Risco de ban + perda de voz autoral.

## Core Value

Drafts que (a) o Matheus reconhece como dele em 5 segundos de leitura,
(b) o agente DEFENDE com rationale claro ("escolhi este angulo porque seus
ultimos 3 posts de carreira tiveram engagement_rate 2.4x maior que os de
tools, e essa semana voce ainda nao tocou em carreira"), e (c) saem por
um filtro pessimista — se nao convence o critico interno, nao chega ao
usuario.

## Caracter do Agente (Charter)

Sao traits inegociaveis. Mudar requer discussao explicita.

- **Honesto sobre dados ausentes** — se nao sabe quando foi o ultimo post,
  PERGUNTA, nao chuta. Se DB esta vazio, diz isso.
- **Pode recusar** — "nao acho que vale postar hoje" e resposta valida.
  Nao force conteudo so pra justificar a chamada.
- **Mostra raciocinio** — toda recomendacao vem com 2-3 linhas de "por
  que esta escolha agora", referenciando dados concretos.
- **Pessimista no critico** — se duvida que o post passa o "TESTE DE IA"
  ou "TESTE DE UNICIDADE", reescreve antes de mostrar.
- **Tom sobrio** — sem hype, sem "isso vai mudar tudo", sem emoji em
  cada paragrafo. Voz do Matheus, nao voz de coach corporativo.

## Requirements

### Validated

<!-- Phase 0 entregou estes -->

- Estrutura de repo (`app/`, `scripts/`, `templates/`, `tests/`)
- Sessao Playwright persistente reusada do buscarv (`scripts/setup_session.py`)
- Schema SQLite (posts, post_metrics, comments_received, drafts, briefings, themes)
- Gateway `app/repo.py` com CRUD basico
- Smoke tests passando
- Agente Claude Code v0 com REGRA ZERO + 13 fluxos em
  `.claude/agents/linkedin-content-manager.md` (monolitico — sera decomposto em P2-P3)
- `templates/anti_patterns.md` (curto, autoral)
- `templates/post_brief.md` (briefing fillable)

### Active

<!-- Roadmap v1: Phase 1-6 -->

- [ ] Scraper extrai posts + metricas + comentarios e popula DB (P1)
- [ ] Estado situacional automatico a partir do DB (sem perguntar ao usuario o que ja
      esta gravado): "ultimo post foi ha X dias, pilares Y e Z em deficit" (P2a)
- [ ] Pipeline multi-stage com critico iterativo: analyst → strategist → drafter →
      critic → refiner (loop) → presenter (P2b)
- [ ] Voice-match score objetivo (embedding + n-gram) ancorado nos top-K posts (P2b)
- [ ] CLI analytics: melhores horarios/hooks/temas + bench (P3)
- [ ] Imagens (capa) e carrossel PDF (P4)
- [ ] UI Streamlit + cron semanal sem auto-post (P5)
- [ ] Learning loop: predicao de engagement gravada antes; comparacao com real
      apos 7d; ajuste de few-shot weights (P6)

### Out of Scope

- **Auto-publicar no LinkedIn** — LOCKED. Anti-fraud + perda de voz autoral.
- **Multi-user / SaaS** — ferramenta pessoal.
- **Turso / Postgres** — YAGNI ate justificar deploy.
- **ATS / scoring de vagas** — pertence ao repo irmao `buscarv`.
- **Streamlit pages de funil de vagas** — pertencem ao `buscarv`.
- **Geracao de comentarios para outras pessoas** — fica como flow no agente v0
  (`Fluxo: Comentarios`), mas nao tem pipeline dedicado em P2-P6 do v1.

## Context

- Repo irmao do `buscarv`. Reusa o pattern de Playwright + `launch_persistent_context`,
  mas a logica de conteudo e propria.
- Phase 0 (bootstrap) concluida em 2026-05-14.
- O agente atual em `.claude/agents/linkedin-content-manager.md` ja tem a
  inteligencia documentada (REGRA ZERO temporal, anti-padroes, frameworks PAS/SLAY/BAB/AIDA,
  pilares 40/30/20/10, checklist com TESTE DE IA / TESTE DE UNICIDADE).
  O que muda em P2: **decompor o monolito em estagios** rodando como OpenSquad
  squad, e adicionar **critico iterativo** + **voice-match objetivo** + **learning loop**.
- Anthropic SDK + prompt caching: few-shot dos top posts e a parte grande e
  estavel — ideal para cache. Critic/refiner sao chamadas curtas.
- Arquitetura detalhada em `.planning/ARCHITECTURE.md`.

## Constraints

- **Tech stack**: Python 3.13+, Playwright sync, SQLite local, Anthropic SDK,
  Pillow (imagens), fal.ai (capas opcionais), pytest+ruff+black
- **Runtime do produto**: OpenSquad (Node.js 20+) para orquestrar squad multi-stage
  com checkpoints — instalado via `npx opensquad init`. Stages chamam scripts Python.
- **Build do projeto**: GSD (discuss → plan → execute por phase)
- **Operacional**: scrape ≤ 2 runs/semana, intervalos randomicos, UA normal
- **Seguranca / PII**: `.browser_profile/` e `data/*.sqlite3` gitignored
- **Estilo de saida**: drafts NAO podem casar `templates/anti_patterns.md`
- **Critico em v1**: so `anti_pattern_pass` e BLOQUEANTE (regex duro).
  voice_match, hook_strength, specificity, predicted_engagement aparecem
  como SCORES INFORMATIVOS com rationale, mas nao bloqueiam — calibracao
  para gates duros acontece em P6 com dados reais de engagement
- **Plataforma alvo**: Windows (dev local), Chromium via Playwright

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Repo separado do `buscarv` | Conteudo vs vagas sao dominios distintos | ✓ Good |
| SQLite local (vs Turso/Postgres) | Single-user, sem deploy, simples | — Pending |
| NUNCA auto-postar | LinkedIn anti-fraud + voz autoral | ✓ LOCKED |
| Claude API com prompt caching | Few-shot grande e estavel = ideal pra cache | — Pending (P2) |
| Playwright sync + persistent_context | Reusa sessao logada, padrao do buscarv | ✓ Good |
| GSD para build do projeto | Estrutura phase + checkpoints | — Pending |
| **Runtime via OpenSquad multi-stage**, NAO subagent monolitico | Cada estagio tem contexto proprio + checkpoint humano + e auditavel separadamente. Decompor o monolito reduz drift e melhora critico iterativo. | — Pending (P2b) |
| **Critico iterativo, nao filtro single-pass** | Filtro descarta; critico iterativo refina ate passar (max 3 iter). Maximiza yield sem afrouxar qualidade. | — Pending (P2b) |
| **Scores informativos em v1; gates duros em P6 com calibracao** | Threshold sem dados de calibracao seria chute. So `anti_pattern_pass` bloqueia em v1 (regex e determinístico). Outras dims acumulam dados de feedback humano + engagement real ate ter base pra threshold defendivel. | — Pending (P2b → P6) |
| **Voice-match LLM-based primeiro, embeddings deferidos** | LLM critic le top-K + draft e emite score+rationale. Sem dep de embedding model. Se em P6 a calibracao mostrar valor, considerar adicionar score quantitativo. | — Pending (P2b) |
| **Learning loop (predict → measure → update)** | Sem isso, o critico nunca melhora. Engagement real e a ground truth. | — Pending (P6) |
| **Agente le DB, nao pergunta** o que ja esta gravado | REGRA ZERO foi escrita assumindo browser/usuario; com DB populado pela P1, o agente sabe. So pergunta o que NAO esta no DB. | — Pending (P2a) |
| Selectors do LinkedIn precisam de spike DOM antes de codar | DOM muda; inspecionar via Playwright MCP primeiro | — Pending (P1) |

---
*Last updated: 2026-05-14 after re-evaluation: previous plan treated agent as template-generator; revised to multi-stage reasoning pipeline with self-critique loop and learning feedback.*
