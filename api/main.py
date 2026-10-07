"""
FastAPI backend: exposes the SQL analytics as JSON endpoints.

Run:  uvicorn api.main:app --reload
Docs: http://localhost:8000/docs   (interactive, auto-generated)
"""
from typing import Annotated, Optional

from fastapi import Depends, FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.db import run_query

app = FastAPI(
    title="Product Analytics API",
    version="1.0.0",
    description="Revenue, AOV, product performance, funnel, cohort, retention and RFM analytics "
                "computed in SQL over the Olist e-commerce dataset.",
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET"], allow_headers=["*"])


@app.exception_handler(FileNotFoundError)
async def db_missing(_: Request, exc: FileNotFoundError):
    return JSONResponse(status_code=503, content={"detail": str(exc)})


def filters(
    start: Annotated[Optional[str], Query(pattern=r"^\d{4}-\d{2}$", description="First month, YYYY-MM")] = None,
    end: Annotated[Optional[str], Query(pattern=r"^\d{4}-\d{2}$", description="Last month, YYYY-MM")] = None,
    state: Annotated[Optional[str], Query(min_length=2, max_length=2, description="Customer state, e.g. SP")] = None,
) -> dict:
    """Shared query parameters, validated by FastAPI before our code runs."""
    return {"start": start, "end": end, "state": state.upper() if state else None}


Filters = Annotated[dict, Depends(filters)]


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok"}


@app.get("/meta", tags=["system"], summary="Available states and months (for filter widgets)")
def meta():
    return run_query("meta")


@app.get("/kpis", tags=["metrics"], summary="Revenue, orders, customers, AOV")
def kpis(f: Filters):
    return run_query("kpis", f)[0]


@app.get("/revenue/monthly", tags=["metrics"], summary="Monthly revenue, AOV and MoM growth")
def revenue_monthly(f: Filters):
    return run_query("revenue_monthly", f)


@app.get("/products/top", tags=["metrics"], summary="Top product categories by revenue")
def top_products(f: Filters, limit: Annotated[int, Query(ge=1, le=100)] = 10):
    return run_query("top_products", f)[:limit]


@app.get("/funnel", tags=["analyses"], summary="Order-fulfilment funnel")
def funnel(f: Filters):
    return run_query("funnel", f)


@app.get("/cohorts", tags=["analyses"], summary="Cohort retention matrix (long format)")
def cohorts():
    return run_query("cohort")


@app.get("/retention/summary", tags=["analyses"], summary="Repeat-purchase rate")
def retention_summary(f: Filters):
    return run_query("retention", f)[0]


@app.get("/rfm", tags=["analyses"], summary="RFM customer segments")
def rfm():
    return run_query("rfm")


@app.get("/geography", tags=["metrics"], summary="Sales by state")
def geography(f: Filters):
    return run_query("geography", f)


@app.get("/delivery", tags=["metrics"], summary="Delivery time, late % and review score by month")
def delivery(f: Filters):
    return run_query("delivery", f)


@app.get("/payments", tags=["metrics"], summary="Payment method mix")
def payments(f: Filters):
    return run_query("payments", f)
