"""PostRepo — gateway unico pra persistencia SQLite.

Pattern adaptado do `app/repo.py` do buscarv. Mantem regra: o repo nao expoe
detalhes de SQL pro resto da app; chamador trabalha com dicts/dataclasses.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_DB_PATH = Path("data/linkedin.sqlite3")

VALID_DRAFT_STATUSES = frozenset({"generated", "approved", "published", "discarded"})
VALID_MEDIA_TYPES = frozenset({"text", "image", "carousel", "video", "article"})


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    if not db_path.exists():
        raise FileNotFoundError(
            f"DB nao existe em {db_path}. Rode `python scripts/init_db.py` primeiro."
        )
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# === Posts =====================================================================

def upsert_post(
    post_id: str,
    *,
    url: str | None,
    posted_at: str,
    text: str,
    media_type: str = "text",
    theme: str | None = None,
    hook_pattern: str | None = None,
    db_path: Path = DEFAULT_DB_PATH,
) -> None:
    if media_type not in VALID_MEDIA_TYPES:
        raise ValueError(f"media_type invalido: {media_type}")
    conn = _connect(db_path)
    try:
        conn.execute(
            """
            INSERT INTO posts (post_id, url, posted_at, text, media_type, theme, hook_pattern, scraped_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(post_id) DO UPDATE SET
                url=excluded.url,
                text=excluded.text,
                media_type=excluded.media_type,
                theme=COALESCE(excluded.theme, posts.theme),
                hook_pattern=COALESCE(excluded.hook_pattern, posts.hook_pattern),
                scraped_at=excluded.scraped_at
            """,
            (post_id, url, posted_at, text, media_type, theme, hook_pattern, _now_iso()),
        )
        conn.commit()
    finally:
        conn.close()


def list_posts(limit: int = 50, db_path: Path = DEFAULT_DB_PATH) -> list[dict[str, Any]]:
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            "SELECT * FROM posts ORDER BY posted_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# === Drafts ====================================================================

def create_draft(
    *,
    text: str,
    theme: str | None = None,
    hook_pattern: str | None = None,
    notes: str | None = None,
    db_path: Path = DEFAULT_DB_PATH,
) -> int:
    conn = _connect(db_path)
    try:
        cur = conn.execute(
            """
            INSERT INTO drafts (created_at, status, theme, hook_pattern, text, notes)
            VALUES (?, 'generated', ?, ?, ?, ?)
            """,
            (_now_iso(), theme, hook_pattern, text, notes),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def update_draft_status(draft_id: int, status: str, db_path: Path = DEFAULT_DB_PATH) -> None:
    if status not in VALID_DRAFT_STATUSES:
        raise ValueError(f"status invalido: {status}")
    conn = _connect(db_path)
    try:
        conn.execute(
            "UPDATE drafts SET status = ? WHERE draft_id = ?", (status, draft_id)
        )
        conn.commit()
    finally:
        conn.close()


def list_drafts(status: str | None = None, db_path: Path = DEFAULT_DB_PATH) -> list[dict[str, Any]]:
    conn = _connect(db_path)
    try:
        if status:
            rows = conn.execute(
                "SELECT * FROM drafts WHERE status = ? ORDER BY created_at DESC",
                (status,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM drafts ORDER BY created_at DESC"
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# === Metrics ===================================================================

def record_metrics(
    post_id: str,
    *,
    reactions: int = 0,
    comments: int = 0,
    shares: int = 0,
    impressions: int | None = None,
    db_path: Path = DEFAULT_DB_PATH,
) -> None:
    engagement = None
    if impressions and impressions > 0:
        engagement = (reactions + comments + shares) / impressions
    conn = _connect(db_path)
    try:
        conn.execute(
            """
            INSERT OR REPLACE INTO post_metrics
            (post_id, captured_at, reactions, comments, shares, impressions, engagement_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (post_id, _now_iso(), reactions, comments, shares, impressions, engagement),
        )
        conn.commit()
    finally:
        conn.close()
