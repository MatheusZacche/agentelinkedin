# Architecture: linkedin-content-agent

> Como o agente raciocina. Documento vivo. Atualizar quando estagios mudarem.

## Princípios

1. **Pensa antes de gerar** — diagnostico e estrategia precedem qualquer
   chamada de geracao de texto.
2. **Multi-stage, nao monolito** — cada estagio tem contexto, output e
   responsabilidade proprios; pode ser auditado em isolamento.
3. **Critico iterativo, nao filtro single-pass** — drafts ruins voltam para
   refinamento com feedback estruturado, max N iteracoes.
4. **Ancorado em dados reais** — pulls de SQLite (Phase 1 output);
   nao re-pergunta o que ja foi gravado.
5. **Pessimista por default** — se duvida, recusa ou itera. Yield baixo
   e aceitavel; falso positivo (post ruim publicado) nao e.
6. **Aprende com a realidade** — engagement previsto vs real fecha o loop
   em P6, e e o que vai transformar scores informativos em gates duros.

## Composicao do squad (run-time = OpenSquad: `linkedin-weekly`)

**5 estagios bloqueantes** rodam sempre, **2 condicionais** dependem do tipo
de post, **1 assincrono** roda separado 7d depois.

```
   trigger
      │
      ▼
┌──────────────────┐  STAGE 1 (auto, sem checkpoint)
│ social-analyst   │  le SQLite + relogio → SITUACAO_ATUAL
└────────┬─────────┘
         │ situacao.json
         ▼
┌──────────────────┐  STAGE 2 (CHECKPOINT 1)
│ editorial-       │  decide tema/pilar/formato/framework,
│ strategist       │  OU recusa ("nao vale postar hoje, sugiro quinta")
└────────┬─────────┘
         │ strategy.md          ◄── usuario aprova / redireciona / encerra
         ▼
┌──────────────────┐  STAGE 3 (auto, sem checkpoint)
│ copywriter       │  N=5 variacoes com angulos distintos,
│                  │  ancoradas em few-shot top-K (cache hit)
└────────┬─────────┘
         │ drafts/v01.md ... v05.md
         ▼
┌──────────────────┐  STAGE 4 (auto, loop interno editor⇄rewriter)
│ editor           │  pontua 5 dimensoes; emite edit_notes
│      ⇄           │
│ rewriter         │  refaz draft focado em dimensoes falhas
│                  │  max 3 iteracoes por draft
└────────┬─────────┘
         │ drafts/v0N-rM.md + scores/v0N-rM.json
         ▼
┌──────────────────┐  STAGE 5 (CHECKPOINT 2)
│ presenter        │  ranqueia drafts que passaram (anti_pattern_pass=True);
│                  │  exibe top 3 com score breakdown + rationale
└────────┬─────────┘
         │              ◄── usuario escolhe 1 / pede regenerar / abandona
         ▼
┌──────────────────┐  CONDICIONAL 1 (CHECKPOINT 3, so se formato != texto puro)
│ art-director     │  decide tipo de visual, gera brief,
│                  │  opcionalmente chama fal.ai ou Pillow scripts
└────────┬─────────┘
         │              ◄── usuario aprova package texto+visual
         ▼
┌──────────────────┐  CONDICIONAL 2 (auto, DB write)
│ archivist        │  grava draft.status=approved + predicted_score +
│                  │  cria todo "medir engagement +7d"
└──────────────────┘

           [+7d, ASSINCRONO]
┌──────────────────┐  STAGE 9 (cron / Streamlit button / GitHub Action)
│ performance-     │  pede URL ou scrape; pull post_metrics real;
│ analyst          │  compara predicted vs real → grava em
│                  │  model_calibration. Em P6, isso vira gates duros.
└──────────────────┘
```

## Estagios em detalhe

### STAGE 1 — social-analyst (auto)

**Input**: hora atual, ultimos 30d de `posts` + `post_metrics` no DB
**Lê**:
- `posts` filtrados por user_id e posted_at >= now() - 30d
- `post_metrics` mais recente por post (window function)
- `comments_received` agrupados por post → temas que audiencia comentou
**Computa**:
- Dias desde ultimo post
- Distribuicao real de pilares vs ideal 40/30/20/10
- Top-K (default K=5) posts por `engagement_rate`
- Hooks usados nos top posts (regex sobre primeiras 2 linhas)
- Temas em deficit (pilar nao tocado em >7d)
- Janela de postagem (tabela horaria do agente v0)
**Output**: `situacao.json`
```json
{
  "now": "2026-05-14T14:32:00-03:00",
  "weekday": "thursday",
  "window_status": "closed",
  "last_post": {"date": "2026-05-12", "pilar": "automacao", "engagement_rate": 0.043},
  "days_since_last": 2,
  "pillar_distribution_30d": {"automacao": 0.55, "bi": 0.30, "carreira": 0.10, "tendencias": 0.05},
  "ideal": {"automacao": 0.40, "bi": 0.30, "carreira": 0.20, "tendencias": 0.10},
  "gaps": ["carreira: 7+ dias sem post"],
  "top_hooks_30d": ["cena especifica com hora", "vulnerabilidade tecnica", ...],
  "audience_themes_via_comments": ["transicao de carreira", "Power BI custom visuals"],
  "top_k_posts": [{"urn": "...", "engagement_rate": 0.082, "text": "..."}, ...]
}
```

**Recusa**: se DB esta vazio ou mais antigo que 7 dias, retorna erro estruturado pedindo scrape primeiro — NAO chuta.

### STAGE 2 — editorial-strategist (CHECKPOINT 1)

**Input**: `situacao.json` + briefing opcional (`templates/post_brief.md`) + `references/perfil.md`
**Decide**:
- Vale postar hoje? Se nao, `decision: defer` com proxima data ideal
- Pilar e angulo (baseado em gap + briefing + audience_themes)
- Formato (texto / texto+imagem / carrossel / enquete)
- Framework de copy (PAS / SLAY / BAB / AIDA / livre)
- `predicted_engagement_prior` baseado em media historica do pilar+horario+framework
**Output**: `strategy.md` com seccoes: Decisao, Por que agora, Por que este angulo, Predicao, Riscos
**Checkpoint 1**: usuario aprova / redireciona / encerra. Se `defer`, fim do pipeline.

### STAGE 3 — copywriter (auto)

**Input**: `strategy.md` + `situacao.json.top_k_posts` (few-shot) + briefing
**Geracao**: N=5 variacoes com ANGULOS DISTINTOS (nao 5 quase-iguais).
**Otimizacao**: top-K few-shot enviado com `cache_control` → cache hit nas N chamadas
**Output**: `drafts/v01.md` ... `drafts/v05.md` com frontmatter
`{angle, framework, hook_type, predicted_score}`

### STAGE 4 — editor ⇄ rewriter (loop interno, max 3 iter por draft)

Um unico estagio do squad com loop interno. Para cada draft em paralelo:

**Editor pontua 5 dimensoes [0..1]**:

| Dim | Metodo (v1) | Bloqueante? |
|-----|-------------|-------------|
| `voice_match` | LLM critic le top-K posts + draft; emite score 0..1 + rationale | **Informativo** em v1; calibrado em P6 |
| `hook_strength` | LLM critic julga primeiras 2 linhas: tem cena/numero/nome especifico? Casa hook proibido? | Informativo; calibrado em P6 |
| `specificity` | Conta numeros + nomes proprios + nomes de tools / paragrafos | Informativo |
| `anti_pattern_pass` | Regex contra `templates/anti_patterns.md` (hooks/vocab/estruturas) | **BLOQUEANTE** desde v1 |
| `predicted_engagement` | Bayesian a posteriori: pilar+horario+framework+hook_type → engagement_rate esperado | Informativo |

**Regra v1**: so `anti_pattern_pass == False` rejeita. Outras dimensoes
mostram score + rationale, MAS nao bloqueiam — a calibracao desses gates
acontece em P6 com dados reais de engagement.

**Rewriter**: se `anti_pattern_pass == False` OU se editor sinalizou
`needs_revision: true` no rationale (julgamento subjetivo do critic),
rewrite focado nas dimensoes flagadas. Preserva o que ja passou.

**Termina**: anti_pattern_pass passa OU 3 iteracoes. Apos 3 sem passar →
`status: rejected_final`.

**Output**: `drafts/v0N-rM.md` + `scores/v0N-rM.json`

### STAGE 5 — presenter (CHECKPOINT 2)

**Input**: pool de drafts com `anti_pattern_pass == True`
**Rank**: por `predicted_engagement` desempatando por `voice_match` informativo
**Output**: PT-BR. Ate 3 drafts top com texto completo + score breakdown
(scores aparecem mesmo nao sendo bloqueantes, pra calibrar com feedback humano)
+ 1 frase de "por que este e melhor".

**Checkpoint 2**: usuario escolhe 1 / pede regenerar / abandona.

### CONDICIONAL 1 — art-director (CHECKPOINT 3, so se nao for texto puro)

So roda se `strategy.formato != "texto"`.
Decide tipo de visual (destaque / comparativo / lista / diagrama / carrossel
8 slides). Gera brief. Opcionalmente chama `scripts/gen_image.py` ou
`scripts/gen_carousel.py`.
**Checkpoint 3**: usuario aprova package final (texto + visual).

### CONDICIONAL 2 — archivist (auto, DB write)

Grava em DB:
- `drafts` row com `status=approved`, texto final, `predicted_score`
- `briefings` row + `draft_briefings` link
- Cria todo "medir engagement em 7d" com `scheduled_for=date+7`

Sem checkpoint — e write determinístico.

### STAGE 9 — performance-analyst (ASSINCRONO, +7d)

Trigger: cron / GitHub Action / botao no Streamlit
**Input**: drafts com `status=approved` e `scheduled_for <= today`
**Acoes**:
- Pede ao usuario URL do post publicado (ou usa scrape autenticado)
- Pull `post_metrics` desse post
- Compara `predicted_score` vs `actual_engagement_rate`
- Loga miss em `model_calibration` table
- Recalcula top-K (posts antigos perdem peso)
- **Em P6**: se acumular dados suficientes, propoe transformar scores
  informativos (voice_match/hook_strength/specificity/predicted_engagement)
  em gates duros com threshold calibrado a partir dos dados reais
- Se draft passou critico mas post bombou → sugere adicao ao `anti_patterns.md`
  (com aprovacao humana antes de gravar)

## Artefatos por execucao

Cada chamada do pipeline cria pasta em `data/runs/<YYYY-MM-DD-slug>/`:

```
runs/2026-05-15-carreira-junior/
├── situacao.json
├── strategy.md
├── drafts/
│   ├── v01.md
│   ├── v01-r1.md
│   ├── v02.md
│   └── ...
├── scores/
│   ├── v01.json
│   ├── v01-r1.json
│   └── ...
├── final.md          # o que o usuario escolheu
├── visual/           # se aplicavel
│   ├── brief.md
│   └── cover.png
└── outcome.json      # preenchido em +7d pelo performance-analyst
```

## Mapeamento implementacao → phases GSD

| Phase | O que entrega |
|-------|---------------|
| P1 | Scraper + loader → `posts` / `post_metrics` / `comments_received` populados |
| P2a | social-analyst + `situacao.json` + acesso ao DB |
| P2b | editorial-strategist + copywriter + editor⇄rewriter (loop) + presenter; few-shot com prompt cache; scores informativos (so anti_pattern_pass bloqueia) |
| P3 | CLI analytics (substrato compartilhado com social-analyst); benchmark opcional contra perfis admirados |
| P4 | art-director + scripts de imagem/carrossel via fal.ai/Pillow |
| P5 | Streamlit pipeline view; cron de scrape semanal; **OpenSquad instalado e rodando squad fim-a-fim** |
| P6 | performance-analyst (assincrono); ajuste de few-shot weights; sugestoes de update do `anti_patterns.md`; **calibracao de thresholds para transformar scores informativos em gates duros** |

## O que NAO esta nesta arquitetura

- Geracao de comentarios para posts de terceiros (existe como Fluxo no v0
  do agente em `.claude/agents/linkedin-content-manager.md`, fora do pipeline weekly)
- Geracao de calendario editorial em batch — pode ser feito rodando o
  pipeline N vezes, sem squad proprio em v1
- Auto-publicacao — fora de escopo (LOCKED)
- Voice-match via embeddings — deferido; comeca como LLM critic subjetivo.
  Se em P6 mostrar valor, considerar adicionar score quantitativo

---
*Created: 2026-05-14. Revisado pos-decisoes do usuario: scores informativos primeiro (so anti-pattern bloqueia), squad 5+2+1, voice-match LLM-based (embeddings deferidos), learning loop como P6 separado.*
