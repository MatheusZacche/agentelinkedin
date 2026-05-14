# Requirements: linkedin-content-agent

**Defined:** 2026-05-14
**Last revised:** 2026-05-14 (multi-stage reasoning pipeline, post user feedback)
**Core Value:** Drafts que o Matheus reconhece como dele em 5s, que o agente defende com rationale claro, e que so chegam ao usuario apos passar critico pessimista.

> Arquitetura detalhada em `.planning/ARCHITECTURE.md`.

## v1 Requirements

Cada requirement mapeia para um phase no `.planning/ROADMAP.md`.

### Scrape (P1)

- [ ] **SCRAPE-01**: Scraper abre `/recent-activity/all/` com sessao persistente e faz N scrolls (parametrizavel)
- [ ] **SCRAPE-02**: `_extract_posts` parseia cada card (urn, texto, posted_at, flags de midia) com selectors validados via Playwright MCP spike
- [ ] **SCRAPE-03**: Scraper captura comentarios recebidos por post via endpoint `/feed/update/<urn>/...`
- [ ] **SCRAPE-04**: Save-as-you-go: JSON parcial gravado a cada batch (resiliencia a crash mid-run)
- [ ] **SCRAPE-05**: Spike inicial: inspecao DOM via Playwright MCP gera `references/dom-selectors.md` antes de codar `_extract_posts`

### Metrics (P1)

- [ ] **METRICS-01**: Snapshot de metricas (reactions, comments, shares, impressions opcional) gravado em `post_metrics` por run
- [ ] **METRICS-02**: Loader idempotente: upsert em `posts`, append em `post_metrics` (PK composta permite multiplos snapshots)
- [ ] **METRICS-03**: `engagement_rate` computado: `(reactions + 5*comments + 10*shares) / max(impressions, 100)` — armazenado em view ou coluna gerada

### Reasoning / situacao (P2a) — social-analyst

- [ ] **RZON-01**: `app/analyst.py` lê `posts` + `post_metrics` + `comments_received` dos ultimos 30 dias e emite `situacao.json`
- [ ] **RZON-02**: `situacao.json` inclui: now (ISO), weekday, window_status, last_post (date/pilar/engagement), days_since_last, pillar_distribution_30d vs ideal, gaps, top_hooks_30d, audience_themes
- [ ] **RZON-03**: Janela de postagem (`window_status`) calculada da tabela horaria do agente v0 (vide `linkedin-content-manager.md` Passo 3)
- [ ] **RZON-04**: Quando DB esta vazio ou desatualizado (>7d), analyst RECUSA produzir `situacao.json` e retorna erro estruturado pedindo scrape primeiro — em vez de chutar
- [ ] **RZON-05**: Top-K (default K=5) posts por `engagement_rate` exportados como JSON para uso de few-shot no copywriter

### Strategist (P2b)

- [ ] **STRAT-01**: `app/strategist.py` lê `situacao.json` + briefing opcional + `references/perfil.md` → emite `strategy.md`
- [ ] **STRAT-02**: Strategist pode retornar `decision: defer` com proxima data ideal — se janela fechou, postou ontem, ou usuario ja postou hoje
- [ ] **STRAT-03**: Strategist defende a escolha em 2-3 frases citando dados concretos (gap, deficit por pilar, audience theme)
- [ ] **STRAT-04**: Strategist emite `predicted_engagement` a priori baseado em media historica do pilar+horario+framework

### Draft (P2b) — copywriter

- [ ] **DRAFT-01**: `app/copywriter.py` lê `strategy.md` + top-K few-shot + briefing
- [ ] **DRAFT-02**: Top-K posts injetados como few-shot via Anthropic prompt caching (`cache_control` no message block)
- [ ] **DRAFT-03**: Gera N=5 variacoes COM ANGULOS DISTINTOS (nao 5 quase-iguais); cada draft tem frontmatter `{angle, framework, hook_type, predicted_score}`
- [ ] **DRAFT-04**: Drafts salvos em `data/runs/<date-slug>/drafts/v0N.md`

### Critic (P2b) — editor

- [ ] **CRIT-01**: `app/critic.py` pontua cada draft em 5 dimensoes [0..1]: voice_match, hook_strength, specificity, anti_pattern_pass, predicted_engagement
- [ ] **CRIT-02**: `voice_match` = LLM critic que recebe top-K posts + draft e emite score 0..1 com rationale ("soa como Matheus porque X; mas frase 3 tem cara de coach corporativo"). **Sem dep de embedding model em v1.**
- [ ] **CRIT-03**: `hook_strength` = LLM critic julga primeiras 2 linhas: tem cena/numero/nome especifico? Casa hook proibido em `templates/anti_patterns.md`? Emite 0..1 + rationale
- [ ] **CRIT-04**: **Em v1, apenas `anti_pattern_pass` (regex match) e BLOQUEANTE.** voice_match/hook_strength/specificity/predicted_engagement sao SCORES INFORMATIVOS exibidos ao usuario, sem rejeitar. Calibracao para gates duros acontece em P6.
- [ ] **CRIT-05**: Output: `scores/v0N.json` com breakdown por dimensao + lista de `edit_notes` (acoes especificas a corrigir, se editor sinalizou `needs_revision: true`)

### Refine (P2b) — rewriter loop

- [ ] **REFI-01**: `app/rewriter.py` lê draft rejeitado + scores + edit_notes; faz rewrite focado nas dimensoes flagadas
- [ ] **REFI-02**: Max 3 iteracoes por draft. Apos 3 sem passar `anti_pattern_pass`, marca `status: rejected_final`
- [ ] **REFI-03**: Loop editor⇄rewriter termina quando `anti_pattern_pass == True` E editor nao sinalizou `needs_revision`; cada iteracao salva como `v0N-rM.md`

### Presenter (P2b)

- [ ] **PRES-01**: `app/presenter.py` ranqueia drafts que passaram por `predicted_engagement` (desempate: voice_match)
- [ ] **PRES-02**: Output em PT-BR: ate 3 drafts top com texto completo + score breakdown + 1 frase de "por que este e melhor"

### Analytics (P3)

- [ ] **ANALYTICS-01**: `python -m app.analytics weekly` mostra melhores horarios PARA O USUARIO (nao bench generico)
- [ ] **ANALYTICS-02**: Hooks agrupados por `hook_pattern` (regex de primeiras 2 linhas) e ranqueados por engagement
- [ ] **ANALYTICS-03**: Temas inferidos de `comments_received` ranqueados por volume de comentarios + sentiment
- [ ] **ANALYTICS-04**: Bench opcional: scrape de 5-10 perfis admirados (data analysts BR) e comparativo de hooks/formatos

### Visual (P4) — art-director

- [ ] **IMAGE-01**: `scripts/gen_image.py` chama fal.ai (Nano Banana) com prompt derivado do post
- [ ] **IMAGE-02**: `scripts/gen_carousel.py` exporta PDF de N slides via Pillow, estilo do agente v0 (1080x1350, #1a1a2e, accent #00d4aa)
- [ ] **IMAGE-03**: art-director decide tipo de visual (destaque/comparativo/lista/diagrama) a partir do conteudo

### UX (P5)

- [ ] **UX-01**: Streamlit app exibe pipeline (run em andamento, drafts em iteracao, scores, drafts approved/published)
- [ ] **UX-02**: Cron / GitHub Actions roda scrape semanal nao supervisionado e dispara `social-analyst` para emitir relatorio
- [ ] **UX-03**: NENHUM caminho de codigo publica automaticamente no LinkedIn — verificado por teste de auditoria

### Squad Runtime (P5) — OpenSquad

- [ ] **SQUAD-01**: `npx opensquad init` instalado no repo; `.opensquad/` gitignored se contem state local
- [ ] **SQUAD-02**: Squad `linkedin-weekly` com **5 estagios bloqueantes** (social-analyst → editorial-strategist → copywriter → editor⇄rewriter loop → presenter), **2 condicionais** (art-director se formato != texto; archivist DB write), **1 assincrono** (performance-analyst +7d)
- [ ] **SQUAD-03**: Checkpoints requerem aprovacao humana: CP1 (strategist), CP2 (presenter), CP3 (art-director se aplicavel)
- [ ] **SQUAD-04**: Cada estagio do squad chama o script Python equivalente em `app/*.py` ou cli em `scripts/`

### Learning Loop (P6) — performance-analyst

- [ ] **LEARN-01**: `archivist` grava `predicted_engagement` no DB quando draft e approved
- [ ] **LEARN-02**: `performance-analyst` roda 7d apos approval: pede URL ao usuario ou usa scrape, pull `post_metrics`, compara predicted vs real, grava em `model_calibration`
- [ ] **LEARN-03**: Top-K few-shot recalculado periodicamente (posts antigos perdem peso, novos top entram)
- [ ] **LEARN-04**: Se draft passou critico mas post bombou, performance-analyst sugere adicao ao `templates/anti_patterns.md` (com aprovacao humana antes de gravar)
- [ ] **LEARN-05**: `python -m app.analytics calibration` mostra MAE entre predicted_engagement e real ao longo do tempo

## v2 Requirements

Deferred to future release.

- **COMENTARIO-01**: Squad/pipeline dedicado para gerar comentarios em posts de terceiros (existe como Fluxo no v0, sem pipeline em v1)
- **CALENDARIO-01**: Pipeline em batch para gerar calendario editorial semanal/mensal
- **BENCH-01**: Comparativo automatico entre perfis admirados e o usuario (gap em formatos, pilares)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Auto-publicar no LinkedIn | Anti-fraud da plataforma + perda de voz autoral (LOCKED) |
| Migracao Turso/Postgres | Single-user; YAGNI |
| ATS / scoring de vagas | Pertence ao repo irmao `buscarv` |
| Multi-user / SaaS | Ferramenta pessoal |
| OAuth LinkedIn API publishing | Mesma razao do auto-publicar |
| Treinar embedding model custom | Usar `text-embedding-3-small` ou similar; custom model overkill em v1 |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| SCRAPE-01..05 | P1 | Pending |
| METRICS-01..03 | P1 | Pending |
| RZON-01..05 | P2a | Pending |
| STRAT-01..04 | P2b | Pending |
| DRAFT-01..04 | P2b | Pending |
| CRIT-01..05 | P2b | Pending |
| REFI-01..03 | P2b | Pending |
| PRES-01..02 | P2b | Pending |
| ANALYTICS-01..04 | P3 | Pending |
| IMAGE-01..03 | P4 | Pending |
| UX-01..03 | P5 | Pending |
| SQUAD-01..04 | P5 | Pending |
| LEARN-01..05 | P6 | Pending |

**Coverage:**
- v1 requirements: 39 total
- Mapped to phases: 39
- Unmapped: 0 ✓

---
*Requirements revised: 2026-05-14 apos feedback do usuario para upgrade arquitetural.*
