from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_kpis_are_consistent():
    k = client.get("/kpis").json()
    assert k["orders"] > 0 and k["revenue"] > 0
    assert abs(k["aov"] - k["revenue"] / k["orders"]) < 0.01  # AOV = revenue / orders


def test_monthly_revenue_sums_to_total():
    total = client.get("/kpis").json()["revenue"]
    monthly = client.get("/revenue/monthly").json()
    assert abs(sum(m["revenue"] for m in monthly) - total) < 1


def test_state_filter_reduces_orders():
    all_orders = client.get("/kpis").json()["orders"]
    sp_orders = client.get("/kpis", params={"state": "sp"}).json()["orders"]
    assert 0 < sp_orders < all_orders


def test_date_filter():
    rows = client.get("/revenue/monthly", params={"start": "2017-06", "end": "2017-08"}).json()
    assert [r["month"] for r in rows] == ["2017-06", "2017-07", "2017-08"]


def test_funnel_never_increases():
    counts = [s["orders"] for s in client.get("/funnel").json()]
    assert counts == sorted(counts, reverse=True)


def test_top_products_limit_and_order():
    rows = client.get("/products/top", params={"limit": 5}).json()
    assert len(rows) == 5
    assert [r["revenue"] for r in rows] == sorted((r["revenue"] for r in rows), reverse=True)


def test_cohort_month_zero_is_100_percent():
    zero = [c for c in client.get("/cohorts").json() if c["months_since"] == 0]
    assert zero and all(c["retention_pct"] == 100.0 for c in zero)


def test_rfm_covers_all_customers():
    segs = client.get("/rfm").json()
    assert sum(s["customers"] for s in segs) == client.get("/kpis").json()["customers"]


def test_invalid_filter_rejected():
    assert client.get("/kpis", params={"start": "not-a-date"}).status_code == 422
