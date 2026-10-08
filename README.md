# 📊 Product Analytics Dashboard

End-to-end product analytics project on an e-commerce dataset (100K+ orders): raw CSVs → **SQLite** → **SQL analytics** → **FastAPI** backend → interactive **Streamlit + Plotly** dashboard.

It answers the questions a product/data analyst gets asked every week: *How is revenue trending? Which categories drive sales? Where do orders drop off? Do customers come back? Who are our best customers?*

## Dashboard preview

![Overview](docs/screenshots/overview.png)

| | |
|---|---|
| ![Revenue trends](docs/screenshots/revenue-trends1.png) | ![Delivery and payments](docs/screenshots/revenue-trends2.png) |
| ![Products](docs/screenshots/products1.png) | ![Product concentration](docs/screenshots/products2.png) |
| ![Funnel](docs/screenshots/funnel.png) | ![Cohort retention](docs/screenshots/cohort-retention.png) |
| ![RFM segments](docs/screenshots/rfm-segments1.png) | ![RFM segment details](docs/screenshots/rfm-segments2.png) |

## Architecture

```
 Olist CSVs ──► scripts/load_data.py ──► SQLite (data/olist.db)
                                              │
                                   sql/*.sql  │  one file per analysis
                                              ▼
                                  FastAPI  (api/)   ──  JSON over HTTP, validated filters
                                              │
                                              ▼
                              Streamlit + Plotly (dashboard/)
```

Each layer has one job: **SQL computes, the API serves, the dashboard displays.** The dashboard talks to the API over HTTP and falls back to running the same SQL directly when the API is offline (useful for single-service hosting).

## Metrics and analyses

| Analysis | Definition | SQL file |
|---|---|---|
| Revenue | Sum of item prices on **delivered** orders | `kpis.sql`, `revenue_monthly.sql` |
| AOV | Revenue ÷ distinct orders | `kpis.sql` |
| MoM growth | Revenue vs. previous month (`LAG` window function) | `revenue_monthly.sql` |
| Product performance | Revenue, units, share, Pareto curve by category (`RANK`, windowed sums) | `top_products.sql` |
| Funnel | Purchased → Approved → Shipped → Delivered → Reviewed, from order timestamps | `funnel.sql` |
| Cohort analysis | Cohort = month of first purchase; retention % by months since | `cohort.sql` |
| Retention | Share of customers with more than one order | `retention.sql` |
| RFM segmentation | Recency/Frequency/Monetary scores (`NTILE`) → 7 segments | `rfm.sql` |
| Delivery & satisfaction | Delivery days, late %, review score by month | `delivery.sql` |
| Geography, payments | Sales by state, payment-method mix | `geography.sql`, `payments.sql` |

### Data-modelling decisions worth knowing
- **`customer_unique_id`, not `customer_id`.** In Olist, `customer_id` is regenerated for every order; only `customer_unique_id` identifies a person. Using the wrong one makes every customer look like a one-time buyer.
- **Row fan-out.** Joining `orders` to `order_items` repeats an order once per item, so order counts use `COUNT(DISTINCT order_id)`.
- **Only delivered orders count as revenue.**
- **The funnel follows the order lifecycle**, because the dataset has no click-stream (no views or add-to-cart events).
- **RFM frequency uses fixed rules.** Most customers order exactly once, so frequency quintiles would be meaningless.

## Quick start

Requires **Python 3.10+**.

```bash
git clone https://github.com/shambhavi1410/product-analytics-dashboard
cd product-analytics-dashboard

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**1. Get the data**

Download the [Olist Brazilian E-Commerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) from Kaggle and place the 9 CSV files in `data/raw/`.

*No Kaggle account yet?* Generate a synthetic dataset with the identical schema to try the pipeline:
```bash
python scripts/generate_sample_data.py --orders 20000
```

**2. Build the database**
```bash
python scripts/load_data.py
```

**3. Start the API** (terminal 1)
```bash
uvicorn api.main:app --reload
```
Interactive API docs: http://localhost:8000/docs

**4. Start the dashboard** (terminal 2, with the venv activated)
```bash
streamlit run dashboard/app.py
```

**5. Run the tests**
```bash
pytest
```

## API endpoints

All metric endpoints accept `start` / `end` (`YYYY-MM`) and `state` (e.g. `SP`) filters.

| Endpoint | Returns |
|---|---|
| `GET /kpis` | revenue, orders, customers, AOV |
| `GET /revenue/monthly` | monthly revenue, orders, AOV, MoM growth |
| `GET /products/top?limit=10` | category ranking with revenue share |
| `GET /funnel` | order-fulfilment funnel |
| `GET /cohorts` | cohort retention matrix (long format) |
| `GET /retention/summary` | repeat-purchase rate |
| `GET /rfm` | RFM segment summary |
| `GET /geography` | sales by state |
| `GET /delivery` | delivery days, late %, review score |
| `GET /payments` | payment-method mix |

## Project structure

```
├── data/raw/            # Olist CSVs (not committed)
├── scripts/             # load_data.py, generate_sample_data.py
├── sql/                 # one .sql file per analysis
├── api/                 # FastAPI app (main.py) + DB helper (db.py)
├── dashboard/           # Streamlit app: app.py, utils.py, pages/
└── tests/               # API tests (pytest)
```

## Tech stack
Python · SQL (SQLite, CTEs, window functions) · pandas · FastAPI · Streamlit · Plotly · pytest

## Dataset credit
[Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) (CC BY-NC-SA 4.0). The data is not redistributed in this repository.
