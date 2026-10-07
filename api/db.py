"""Database helper: runs the .sql files in /sql against SQLite and returns plain dicts."""
import os
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SQL_DIR = ROOT / "sql"

# Injected wherever a query contains the /*FILTERS*/ marker. The :names are
# *bound parameters* - SQLite substitutes the values safely (no SQL injection).
# "(:start IS NULL OR ...)" means: if the filter wasn't supplied, ignore it.
FILTERS = """
AND (:start IS NULL OR strftime('%Y-%m', o.order_purchase_timestamp) >= :start)
AND (:end   IS NULL OR strftime('%Y-%m', o.order_purchase_timestamp) <= :end)
AND (:state IS NULL OR c.customer_state = :state)
"""
DEFAULTS = {"start": None, "end": None, "state": None}


def get_db_path() -> Path:
    return Path(os.getenv("DB_PATH", ROOT / "data" / "olist.db"))


def run_query(name: str, params: dict | None = None) -> list[dict]:
    """Run sql/<name>.sql with the given filter params and return a list of row dicts."""
    db_path = get_db_path()
    if not db_path.exists():
        raise FileNotFoundError(
            f"Database not found at {db_path}. Run: python scripts/load_data.py")
    sql = (SQL_DIR / f"{name}.sql").read_text().replace("/*FILTERS*/", FILTERS)
    bound = {**DEFAULTS, **{k: v for k, v in (params or {}).items() if k in DEFAULTS}}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only = ON")  # the API can only READ the database
    try:
        return [dict(r) for r in conn.execute(sql, bound).fetchall()]
    finally:
        conn.close()
