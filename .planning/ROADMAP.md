# Roadmap: linkedin-content-agent

## Overview

Phase 0 (bootstrap) ja entregue em 2026-05-14. As phases 1-6 transformam o
agente monolitico do v0 em um pipeline multi-stage com critico iterativo,
ancoragem em dados reais, e learning loop. Arquitetura completa em
`.planning/ARCHITECTURE.md`.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3, 4, 5, 6): Planned milestone work
- Decimal phases (2.a, 2.b): Splits semanticos da mesma area
- Phase 0 ja entregue

- [x] **Phase 0: Bootstrap** — estrutura, schema, sessao, smoke tests (DONE 2026-05-14)
- [ ] **Phase 1: Coleta funcional** — scraper extrai posts/metricas/comentarios; loader idempotente popula DB
- [ ] **Phase 2a: Estado situacional (analyst)** — social-analyst le DB + relogio → `situacao.json` defensavel
- [ ] **Phase 2b: Pipeline de drafts (strategist + critic loop)** — editorial-strategist, copywriter, editor⇄rewriter loop, presenter; scores informativos com so anti_pattern_pass bloqueando
- [ ] **Phase 3: Analise** — CLI analytics: melhores horarios/hooks/temas, opcional bench contra perfis admirados
- [ ] **Phase 4: Imagens / carrossel** — art-director + scripts fal.ai (capa) + Pillow (PDF carrossel)
- [ ] **Phase 5: UX + Squad fim-a-fim** — Streamlit pipeline view, cron semanal scrape, OpenSquad instalado e rodando squad `linkedin-weekly`
- [ ] **Phase 6: Learning loop** — performance-analyst assincrono, calibracao dos scores informativos para gates duros

## Phase Details

### Phase 1: Coleta funcional
**Goal**: Scraper funcional que puxa atividade recente para SQLite com snapshots de metricas; loader idempotente.
**Depends on**: Phase 0 (done)
**Requirements**: SCRAPE-01..05, METRICS-01..03
**Success Criteria** (what must be TRUE):
  1. `python scripts/scrape_my_activity.py --profile-slug X` extrai N≥10 posts de `/recent-activity/all/`
  2. Cada post capturado tem reactions, comments, shares (impressoes opcional)
  3. Loader e idempotente: upsert em `posts`, append snapshot em `post_metrics`
  4. Comentarios recebidos salvos por post em `comments_received`
  5. `references/dom-selectors.md` gerado a partir de spike Playwright MCP, listando selectors validados
**Plans**: TBD

Plans:
- [ ] 01-TBD: spike DOM + selectors validados
- [ ] 01-TBD: `_extract_posts` + parsing
- [ ] 01-TBD: comentarios por post
- [ ] 01-TBD: loader idempotente
- [ ] 01-TBD: testes integrados

### Phase 2a: Estado situacional (analyst)
**Goal**: `app/analyst.py` produz `situacao.json` defensavel a partir do DB; agente nao re-pergunta o que ja esta gravado.
**Depends on**: Phase 1 (DB com dados reais)
**Requirements**: RZON-01..05
**Success Criteria**:
  1. `python -m app.analyst` emite `situacao.json` com window_status, gaps por pilar, top-K, audience_themes
  2. Se DB esta vazio ou desatualizado (>7d), RECUSA produzir output e pede scrape primeiro (erro estruturado, nao chute)
  3. Top-K posts por engagement_rate exportados para uso de few-shot
**Plans**: TBD

Plans:
- [ ] 02a-TBD: schema do situacao.json + tests
- [ ] 02a-TBD: implementacao do analyst com SQL reads
- [ ] 02a-TBD: tabela de janela de postagem (parametrizavel)

### Phase 2b: Pipeline de drafts (strategist + critic loop)
**Goal**: Pipeline editorial-strategist → copywriter → editor⇄rewriter loop → presenter, com scores informativos e so anti_pattern_pass bloqueando.
**Depends on**: Phase 2a (`situacao.json`)
**Requirements**: STRAT-01..04, DRAFT-01..04, CRIT-01..05, REFI-01..03, PRES-01..02
**Success Criteria**:
  1. `python -m app.strategist` le `situacao.json` + briefing e emite `strategy.md` com Decisao/Por que/Predicao OR `decision: defer`
  2. `python -m app.copywriter` gera N=5 variacoes em `data/runs/<slug>/drafts/v0N.md` com few-shot top-K via prompt caching
  3. `python -m app.critic` pontua 5 dimensoes; emite `scores/v0N.json` com `anti_pattern_pass` (bloqueante) + 4 informativos
  4. `python -m app.rewriter` refaz draft com edit_notes; loop ate passar OU 3 iteracoes
  5. `python -m app.presenter` exibe top 3 drafts que passaram com score breakdown
  6. End-to-end test com briefing real produz drafts validos (anti_pattern_pass) em <60s
**Plans**: TBD

Plans:
- [ ] 02b-TBD: strategist + tests
- [ ] 02b-TBD: copywriter com prompt caching
- [ ] 02b-TBD: critic (5 dimensoes, so anti_pattern bloqueia)
- [ ] 02b-TBD: rewriter + loop control
- [ ] 02b-TBD: presenter

### Phase 3: Analise
**Goal**: CLI analytics surface padroes para o usuario; opcional bench contra perfis admirados.
**Depends on**: Phase 1 (dados) + Phase 2b (drafts/feedback)
**Requirements**: ANALYTICS-01..04
**Success Criteria**:
  1. `python -m app.analytics weekly` exibe melhores horarios PARA O USUARIO
  2. Hooks agrupados por padrao + ranqueados por engagement
  3. Temas inferidos de comments_received ranqueados
  4. (Opcional) Comparativo contra 5-10 perfis admirados
**Plans**: TBD

### Phase 4: Imagens / carrossel
**Goal**: Assets visuais gerados a partir do draft aprovado.
**Depends on**: Phase 2b
**Requirements**: IMAGE-01..03
**Success Criteria**:
  1. `scripts/gen_image.py` produz capa via fal.ai (Nano Banana)
  2. `scripts/gen_carousel.py` exporta PDF de N slides (Pillow, estilo do v0)
  3. art-director decide tipo de visual a partir do conteudo
**Plans**: TBD

### Phase 5: UX + Squad fim-a-fim
**Goal**: Streamlit pipeline view, cron de scrape semanal, OpenSquad instalado e squad `linkedin-weekly` rodando fim-a-fim com 3 checkpoints humanos.
**Depends on**: Phase 2b (pipeline funcionando isolado) + Phase 4 (visuais opcionais)
**Requirements**: UX-01..03, SQUAD-01..04
**Success Criteria**:
  1. Streamlit app exibe pipeline em andamento (drafts em iteracao, scores)
  2. Cron / GitHub Actions roda scrape semanal nao supervisionado
  3. NENHUM caminho de codigo publica automaticamente (teste de auditoria passa)
  4. Squad `linkedin-weekly` definido em OpenSquad com 5 estagios bloqueantes + 2 condicionais + 1 async
  5. Checkpoints CP1/CP2/CP3 funcionam (usuario aprova / redireciona)
**Plans**: TBD

### Phase 6: Learning loop
**Goal**: performance-analyst fecha o ciclo com ground truth; calibra scores informativos para virarem gates duros.
**Depends on**: Phase 5 (squad rodando + dados acumulando)
**Requirements**: LEARN-01..05
**Success Criteria**:
  1. archivist grava `predicted_engagement` quando draft e approved
  2. performance-analyst roda +7d apos approval; pull metrics reais; grava em `model_calibration`
  3. Top-K few-shot recalculado periodicamente
  4. `python -m app.analytics calibration` mostra MAE entre predicted vs real
  5. Apos N=20 drafts publicados, propor thresholds calibrados para voice_match/hook_strength/specificity virarem bloqueantes (com aprovacao humana antes de aplicar)
**Plans**: TBD

## Progress

**Execution Order:**
Phases executam em ordem: 1 → 2a → 2b → 3 → 4 → 5 → 6

| Phase | Plans | Status | Completed |
|-------|-------|--------|-----------|
| 0. Bootstrap | n/a | Complete | 2026-05-14 |
| 1. Coleta funcional | 0/TBD | Not started | - |
| 2a. Estado situacional | 0/TBD | Not started | - |
| 2b. Pipeline de drafts | 0/TBD | Not started | - |
| 3. Analise | 0/TBD | Not started | - |
| 4. Imagens / carrossel | 0/TBD | Not started | - |
| 5. UX + Squad | 0/TBD | Not started | - |
| 6. Learning loop | 0/TBD | Not started | - |
