"""
Generate a SYNTHETIC e-commerce dataset with exactly the same tables and column
names as the public Olist Brazilian E-Commerce dataset.

Why it exists: lets you run the whole project (database -> SQL -> API ->
dashboard) in minutes without a Kaggle account, and powers the automated tests.
For the real project, download the real Olist CSVs into data/raw/ instead.

Usage:
    python scripts/generate_sample_data.py --orders 20000
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

# (portuguese name, english name, typical price in BRL)
CATEGORIES = [
    ("cama_mesa_banho", "bed_bath_table", 90), ("beleza_saude", "health_beauty", 120),
    ("esporte_lazer", "sports_leisure", 110), ("informatica_acessorios", "computers_accessories", 130),
    ("moveis_decoracao", "furniture_decor", 95), ("utilidades_domesticas", "housewares", 80),
    ("relogios_presentes", "watches_gifts", 200), ("telefonia", "telephony", 60),
    ("automotivo", "auto", 115), ("brinquedos", "toys", 85),
    ("cool_stuff", "cool_stuff", 140), ("ferramentas_jardim", "garden_tools", 100),
    ("perfumaria", "perfumery", 105), ("bebes", "baby", 95),
    ("eletronicos", "electronics", 75), ("papelaria", "stationery", 70),
    ("fashion_bolsas_e_acessorios", "fashion_bags_accessories", 110), ("pet_shop", "pet_shop", 90),
    ("livros_interesse_geral", "books_general_interest", 55), ("alimentos", "food", 50),
]
STATES = {"SP": .42, "RJ": .13, "MG": .12, "RS": .055, "PR": .05, "SC": .037, "BA": .034, "DF": .021,
          "GO": .02, "ES": .02, "PE": .017, "CE": .013, "PA": .01, "MT": .01, "MA": .007, "MS": .007}
CITIES = {"SP": ["sao paulo", "campinas"], "RJ": ["rio de janeiro", "niteroi"], "MG": ["belo horizonte", "uberlandia"],
          "RS": ["porto alegre", "caxias do sul"], "PR": ["curitiba", "londrina"], "SC": ["florianopolis", "joinville"],
          "BA": ["salvador", "feira de santana"], "DF": ["brasilia", "taguatinga"], "GO": ["goiania", "anapolis"],
          "ES": ["vitoria", "vila velha"], "PE": ["recife", "olinda"], "CE": ["fortaleza", "sobral"],
          "PA": ["belem", "santarem"], "MT": ["cuiaba", "rondonopolis"], "MA": ["sao luis", "imperatriz"],
          "MS": ["campo grande", "dourados"]}
FMT = "%Y-%m-%d %H:%M:%S"


def hex_ids(rng, n):
    return [rng.bytes(16).hex() for _ in range(n)]


def generate(out_dir, orders=20000, seed=42):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    n = int(orders)

    # ---- geography pool: zip prefixes that belong to a state ----------------
    states = list(STATES)
    sp = np.array(list(STATES.values()))
    sp = sp / sp.sum()
    n_zip = 600
    zip_codes = rng.choice(np.arange(10000, 99999), n_zip, replace=False)
    zip_state = rng.choice(states, n_zip, p=sp)
    zip_city = [CITIES[s][rng.integers(0, 2)] for s in zip_state]
    geolocation = pd.DataFrame({
        "geolocation_zip_code_prefix": zip_codes,
        "geolocation_lat": rng.uniform(-30, -3, n_zip).round(6),
        "geolocation_lng": rng.uniform(-60, -35, n_zip).round(6),
        "geolocation_city": zip_city, "geolocation_state": zip_state})

    # ---- customers: ~3% of orders come from repeat buyers -------------------
    n_unique = int(n * 0.97)
    unique_ids = hex_ids(rng, n_unique)
    uzip = rng.integers(0, n_zip, n_unique)
    order_cust = np.concatenate([np.arange(n_unique), rng.integers(0, n_unique, n - n_unique)])

    # ---- purchase timestamps (growing business Jan-2017 -> Aug-2018) --------
    start, span = pd.Timestamp("2017-01-01"), 607
    first_ts = start + pd.to_timedelta(rng.beta(2.0, 1.4, n_unique) * span, unit="D") \
        + pd.to_timedelta(rng.integers(0, 86400, n_unique), unit="s")
    rep_idx = order_cust[n_unique:]
    rep_ts = first_ts[rep_idx] + pd.to_timedelta(rng.integers(15, 300, len(rep_idx)), unit="D")
    end = start + pd.Timedelta(days=span)
    rep_ts = pd.DatetimeIndex(np.minimum(rep_ts.values, end.to_datetime64()))
    purchase = first_ts.append(rep_ts)

    o = pd.DataFrame({"order_id": hex_ids(rng, n), "customer_id": hex_ids(rng, n),
                      "order_status": rng.choice(["delivered", "shipped", "canceled", "unavailable", "invoiced", "processing"],
                                                 n, p=[.972, .011, .006, .006, .003, .002]),
                      "order_purchase_timestamp": purchase})
    o["order_approved_at"] = o.order_purchase_timestamp + pd.to_timedelta(rng.exponential(8, n) + .2, unit="h")
    o.loc[o.order_status.isin(["canceled", "unavailable"]) & (rng.random(n) < .3), "order_approved_at"] = pd.NaT
    shipped = o.order_status.isin(["delivered", "shipped"])
    o["order_delivered_carrier_date"] = (o.order_approved_at + pd.to_timedelta(rng.uniform(1, 4, n), unit="D")).where(shipped)
    o["order_delivered_customer_date"] = (o.order_delivered_carrier_date
                                          + pd.to_timedelta(rng.gamma(2.5, 4, n) + 1, unit="D")).where(o.order_status == "delivered")
    o["order_estimated_delivery_date"] = o.order_purchase_timestamp + pd.to_timedelta(
        np.clip(rng.normal(26, 5, n), 12, 50).round(), unit="D")

    customers = pd.DataFrame({
        "customer_id": o.customer_id, "customer_unique_id": [unique_ids[i] for i in order_cust],
        "customer_zip_code_prefix": zip_codes[uzip[order_cust]],
        "customer_city": [zip_city[i] for i in uzip[order_cust]],
        "customer_state": zip_state[uzip[order_cust]]})

    # ---- catalog -------------------------------------------------------------
    n_prod, n_sell = 3000, 300
    cw = np.array([1 / (i + 1) ** .8 for i in range(len(CATEGORIES))])
    cw /= cw.sum()
    pcat = rng.choice(len(CATEGORIES), n_prod, p=cw)
    scale = np.array([c[2] for c in CATEGORIES])
    base_price = np.exp(rng.normal(np.log(scale[pcat]), .6))
    prod_ids = hex_ids(rng, n_prod)
    products = pd.DataFrame({
        "product_id": prod_ids, "product_category_name": [CATEGORIES[i][0] for i in pcat],
        "product_name_lenght": rng.integers(20, 60, n_prod), "product_description_lenght": rng.integers(100, 1500, n_prod),
        "product_photos_qty": rng.integers(1, 6, n_prod), "product_weight_g": rng.integers(100, 5000, n_prod),
        "product_length_cm": rng.integers(10, 60, n_prod), "product_height_cm": rng.integers(5, 40, n_prod),
        "product_width_cm": rng.integers(10, 50, n_prod)})
    sell_state = rng.choice(states, n_sell, p=sp)
    sellers = pd.DataFrame({
        "seller_id": hex_ids(rng, n_sell), "seller_zip_code_prefix": rng.choice(zip_codes, n_sell),
        "seller_city": [CITIES[s][0] for s in sell_state], "seller_state": sell_state})
    translation = pd.DataFrame({"product_category_name": [c[0] for c in CATEGORIES],
                                "product_category_name_english": [c[1] for c in CATEGORIES]})

    # ---- order items ---------------------------------------------------------
    k = rng.choice([1, 2, 3, 4], n, p=[.88, .09, .025, .005])
    item_order = np.repeat(np.arange(n), k)
    item_no = np.concatenate([np.arange(1, x + 1) for x in k])
    pop = rng.pareto(1.5, n_prod) + 1
    pop /= pop.sum()
    pidx = rng.choice(n_prod, len(item_order), p=pop)
    prod_seller = rng.integers(0, n_sell, n_prod)
    price = np.maximum(3, np.round(base_price[pidx] * rng.uniform(.85, 1.15, len(pidx)), 2))
    freight = np.round(7 + price * rng.uniform(.03, .12, len(pidx)) + rng.exponential(5, len(pidx)), 2)
    items = pd.DataFrame({
        "order_id": o.order_id.to_numpy()[item_order], "order_item_id": item_no,
        "product_id": np.array(prod_ids)[pidx], "seller_id": sellers.seller_id.to_numpy()[prod_seller[pidx]],
        "shipping_limit_date": (o.order_purchase_timestamp.to_numpy()[item_order] + np.timedelta64(3, "D")),
        "price": price, "freight_value": freight})
    items["shipping_limit_date"] = pd.to_datetime(items.shipping_limit_date).dt.strftime(FMT)

    # ---- payments ------------------------------------------------------------
    total = (items.groupby("order_id")[["price", "freight_value"]].sum().sum(axis=1)).reindex(o.order_id).to_numpy()
    ptype = rng.choice(["credit_card", "boleto", "voucher", "debit_card"], n, p=[.74, .19, .055, .015])
    inst = np.where(ptype == "credit_card",
                    rng.choice(np.arange(1, 11), n, p=[.5, .1, .1, .07, .05, .04, .03, .03, .02, .06]), 1)
    payments = pd.DataFrame({"order_id": o.order_id, "payment_sequential": 1, "payment_type": ptype,
                             "payment_installments": inst, "payment_value": np.round(total, 2)})

    # ---- reviews (late deliveries get worse scores) --------------------------
    d = o[o.order_status == "delivered"]
    d = d[rng.random(len(d)) < .985]
    late = (d.order_delivered_customer_date > d.order_estimated_delivery_date).to_numpy()
    good = rng.choice([1, 2, 3, 4, 5], len(d), p=[.07, .03, .08, .19, .63])
    bad = rng.choice([1, 2, 3, 4, 5], len(d), p=[.45, .15, .18, .12, .10])
    created = d.order_delivered_customer_date + pd.to_timedelta(rng.integers(1, 6, len(d)), unit="D")
    reviews = pd.DataFrame({
        "review_id": hex_ids(rng, len(d)), "order_id": d.order_id.to_numpy(),
        "review_score": np.where(late, bad, good), "review_comment_title": np.nan, "review_comment_message": np.nan,
        "review_creation_date": created.dt.strftime(FMT).to_numpy(),
        "review_answer_timestamp": (created + pd.to_timedelta(rng.integers(1, 4, len(d)), unit="D")).dt.strftime(FMT).to_numpy()})

    for col in ["order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date",
                "order_delivered_customer_date", "order_estimated_delivery_date"]:
        o[col] = o[col].dt.strftime(FMT)

    files = {"olist_customers_dataset.csv": customers, "olist_orders_dataset.csv": o,
             "olist_order_items_dataset.csv": items, "olist_order_payments_dataset.csv": payments,
             "olist_order_reviews_dataset.csv": reviews, "olist_products_dataset.csv": products,
             "olist_sellers_dataset.csv": sellers, "olist_geolocation_dataset.csv": geolocation,
             "product_category_name_translation.csv": translation}
    for name, df in files.items():
        df.to_csv(out / name, index=False)
    print(f"Wrote {len(files)} synthetic CSVs ({n:,} orders) to {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="data/raw")
    ap.add_argument("--orders", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    generate(a.out, a.orders, a.seed)
