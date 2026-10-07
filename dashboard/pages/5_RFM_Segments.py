import plotly.express as px
import streamlit as st
from utils import brl, fetch, num, setup

setup("RFM Segments", "👥")
st.title("👥 RFM Customer Segmentation")
st.caption("Recency (days since last order) · Frequency (number of orders) · Monetary (total spend).")
df = fetch("rfm")

a, b = st.columns(2)
with a:
    st.subheader("Customers per segment")
    st.plotly_chart(px.treemap(df, path=["segment"], values="customers", color="avg_monetary",
                               color_continuous_scale="Blues"), width="stretch")
with b:
    st.subheader("Revenue per segment")
    fig = px.bar(df.sort_values("total_revenue"), x="total_revenue", y="segment", orientation="h",
                 labels={"total_revenue": "Revenue (R$)"})
    st.plotly_chart(fig, width="stretch")

st.dataframe(df, width="stretch", hide_index=True)
top = df.iloc[0]
st.info(f"**{top.segment}** is the largest revenue source: {brl(top.total_revenue)} "
        f"from {num(top.customers)} customers ({top.pct_customers}% of the base).")

with st.expander("How segments are defined"):
    st.markdown("""
Each customer gets R, F and M scores from 1 (worst) to 5 (best). R and M use quintiles (`NTILE(5)`);
F uses fixed rules (1 order → 1, 2 orders → 3, 3+ → 5) because most customers order only once.

| Segment | Rule |
|---|---|
| Champions | R ≥ 4 and F ≥ 3 |
| Loyal Customers | F ≥ 3 |
| New High-Value | R ≥ 4 and M ≥ 4 |
| Recent Buyers | R ≥ 4 |
| At Risk (High-Value) | R ≤ 2 and M ≥ 4 |
| Hibernating | R ≤ 2 |
| Needs Attention | everyone else |
""")
