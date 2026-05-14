"""Inicializa o SQLite local rodando o schema.sql.

Uso:
    python scripts/init_db.py
    python scripts/init_db.py --db data/linkedin.sqlite3 --schema app/db/schema.sql
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", type=Path, default=Path("data/linkedin.sqlite3"))
    ap.add_argument("--schema", type=Path, default=Path("app/db/schema.sql"))
    args = ap.parse_args()

    args.db.parent.mkdir(parents=True, exist_ok=True)
    sql = args.schema.read_text(encoding="utf-8")
    conn = sqlite3.connect(args.db)
    try:
        conn.executescript(sql)
        conn.commit()
    finally:
        conn.close()
    print(f"OK. DB criado/atualizado em {args.db}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
