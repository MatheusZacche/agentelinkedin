"""Smoke tests do repo. Nao depende de Playwright nem LinkedIn."""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from app import repo


@pytest.fixture()
def fresh_db(tmp_path: Path) -> Path:
    db = tmp_path / "test.sqlite3"
    schema_sql = Path("app/db/schema.sql").read_text(encoding="utf-8")
    conn = sqlite3.connect(db)
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()
    return db


def test_create_and_list_draft(fresh_db: Path) -> None:
    draft_id = repo.create_draft(text="Hello world", theme="data", db_path=fresh_db)
    assert draft_id > 0
    rows = repo.list_drafts(db_path=fresh_db)
    assert len(rows) == 1
    assert rows[0]["text"] == "Hello world"
    assert rows[0]["status"] == "generated"


def test_update_draft_status(fresh_db: Path) -> None:
    draft_id = repo.create_draft(text="x", db_path=fresh_db)
    repo.update_draft_status(draft_id, "approved", db_path=fresh_db)
    rows = repo.list_drafts(status="approved", db_path=fresh_db)
    assert len(rows) == 1


def test_upsert_post_idempotent(fresh_db: Path) -> None:
    repo.upsert_post(
        "urn:li:activity:1",
        url="https://linkedin.com/x",
        posted_at="2026-05-01T10:00:00Z",
        text="first",
        db_path=fresh_db,
    )
    repo.upsert_post(
        "urn:li:activity:1",
        url="https://linkedin.com/x",
        posted_at="2026-05-01T10:00:00Z",
        text="updated",
        db_path=fresh_db,
    )
    rows = repo.list_posts(db_path=fresh_db)
    assert len(rows) == 1
    assert rows[0]["text"] == "updated"
