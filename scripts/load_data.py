"""
Load the 9 Olist CSV files into a SQLite database (data/olist.db).

Usage:
    python scripts/load_data.py
    python scripts/load_data.py --raw data/raw --db data/olist.db
"""
import argparse
import sqlite3
from pathlib import Path

import pandas as pd

TABLES = {
    "customers": "olist_customers_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}

# Indexes make the JOINs in our analytics queries fast (like a book's index).
INDEXES = """
CREATE INDEX IF NOT EXISTS idx_orders_customer  ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_status    ON orders(order_status);
CREATE INDEX IF NOT EXISTS idx_orders_purchase  ON orders(order_purchase_timestamp);
CREATE INDEX IF NOT EXISTS idx_items_order      ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_items_product    ON order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_payments_order   ON order_payments(order_id);
CREATE INDEX IF NOT EXISTS idx_reviews_order    ON order_reviews(order_id);
CREATE INDEX IF NOT EXISTS idx_customers_id     ON customers(customer_id);
CREATE INDEX IF NOT EXISTS idx_customers_unique ON customers(customer_unique_id);
CREATE INDEX IF NOT EXISTS idx_customers_state  ON customers(customer_state);
CREATE INDEX IF NOT EXISTS idx_products_id      ON products(product_id);
"""


def load(raw_dir="data/raw", db_path="data/olist.db"):
    raw, db = Path(raw_dir), Path(db_path)
    missing = [f for f in TABLES.values() if not (raw / f).exists()]
    if missing:
        raise SystemExit(
            f"Missing CSV files in {raw}: {missing}\n"
            "Download the Olist dataset from Kaggle into that folder, or run:\n"
            "  python scripts/generate_sample_data.py")
    db.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db)
    for table, file in TABLES.items():
        df = pd.read_csv(raw / file)
        df.to_sql(table, conn, if_exists="replace", index=False, chunksize=50_000)
        print(f"  {table:<22} {len(df):>10,} rows")
    conn.executescript(INDEXES)
    lo, hi = conn.execute(
        "SELECT MIN(order_purchase_timestamp), MAX(order_purchase_timestamp) FROM orders").fetchone()
    print(f"Orders span {lo[:10]} -> {hi[:10]}")
    conn.close()
    print(f"Database ready: {db}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--raw", default="data/raw")
    ap.add_argument("--db", default="data/olist.db")
    a = ap.parse_args()
    load(a.raw, a.db)
