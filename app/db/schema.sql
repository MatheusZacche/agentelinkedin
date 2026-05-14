-- linkedin-content-agent — schema do banco local
-- Use: python scripts/init_db.py
-- SQLite. Migrar pra Turso/Postgres so se virar deploy.

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- Posts ja publicados pelo dono do perfil (raspados ou importados a mao).
CREATE TABLE IF NOT EXISTS posts (
    post_id          TEXT PRIMARY KEY,           -- urn:li:activity:... ou hash
    url              TEXT,
    posted_at        TEXT NOT NULL,              -- ISO8601 UTC
    text             TEXT NOT NULL,
    media_type       TEXT NOT NULL DEFAULT 'text', -- text|image|carousel|video|article
    theme            TEXT,                       -- tag manual ou inferido
    hook_pattern     TEXT,                       -- ex: pergunta, historia, dado, opiniao
    scraped_at       TEXT NOT NULL,
    notes            TEXT
);

-- Metricas no tempo. Um post pode ter varios snapshots (pra ver crescimento).
CREATE TABLE IF NOT EXISTS post_metrics (
    post_id          TEXT NOT NULL,
    captured_at      TEXT NOT NULL,
    reactions        INTEGER DEFAULT 0,
    comments         INTEGER DEFAULT 0,
    shares           INTEGER DEFAULT 0,
    impressions      INTEGER,                    -- pode ser NULL (nem sempre visivel)
    engagement_rate  REAL,                       -- (react+coment+share)/impressions
    PRIMARY KEY (post_id, captured_at),
    FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE
);

-- Comentarios recebidos. Util pra entender o que a audiencia responde.
CREATE TABLE IF NOT EXISTS comments_received (
    comment_id       TEXT PRIMARY KEY,
    post_id          TEXT NOT NULL,
    author           TEXT,
    text             TEXT NOT NULL,
    posted_at        TEXT,
    reactions        INTEGER DEFAULT 0,
    is_reply         INTEGER DEFAULT 0,
    FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE
);

-- Drafts gerados pelo agente. Workflow: gerado -> aprovado -> publicado.
CREATE TABLE IF NOT EXISTS drafts (
    draft_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at       TEXT NOT NULL,
    status           TEXT NOT NULL DEFAULT 'generated', -- generated|approved|published|discarded
    theme            TEXT,
    hook_pattern     TEXT,
    text             TEXT NOT NULL,
    notes            TEXT,
    -- quando publicado, linka pro post real
    published_post_id TEXT,
    FOREIGN KEY (published_post_id) REFERENCES posts(post_id) ON DELETE SET NULL
);

-- Briefings: cada draft costuma vir de um briefing (input do user).
CREATE TABLE IF NOT EXISTS briefings (
    briefing_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at       TEXT NOT NULL,
    topic            TEXT NOT NULL,
    angle            TEXT,                       -- "experiencia pessoal", "dado contrario", etc
    audience         TEXT,                       -- ex: "data analysts BR juniors"
    notes            TEXT
);

CREATE TABLE IF NOT EXISTS draft_briefings (
    draft_id         INTEGER NOT NULL,
    briefing_id      INTEGER NOT NULL,
    PRIMARY KEY (draft_id, briefing_id),
    FOREIGN KEY (draft_id) REFERENCES drafts(draft_id) ON DELETE CASCADE,
    FOREIGN KEY (briefing_id) REFERENCES briefings(briefing_id) ON DELETE CASCADE
);

-- Tags / temas mapeados manualmente.
CREATE TABLE IF NOT EXISTS themes (
    theme            TEXT PRIMARY KEY,
    description      TEXT,
    target_audience  TEXT
);

CREATE INDEX IF NOT EXISTS idx_posts_posted_at ON posts(posted_at DESC);
CREATE INDEX IF NOT EXISTS idx_metrics_captured ON post_metrics(captured_at DESC);
CREATE INDEX IF NOT EXISTS idx_drafts_status ON drafts(status);
