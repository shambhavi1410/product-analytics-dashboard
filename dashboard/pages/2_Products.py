import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from utils import fetch, setup

f = setup("Products", "📦")
st.title("📦 Product Performance")
n = st.slider("Number of categories", 5, 20, 10)
df = fetch("top_products", limit=n, **f)
if df.empty:
    st.warning("No data for these filters.")
    st.stop()

st.subheader(f"Top {n} categories by revenue")
fig = px.bar(df.iloc[::-1], x="revenue", y="category", orientation="h", color="avg_price",
             color_continuous_scale="Blues", labels={"revenue": "Revenue (R$)", "avg_price": "Avg price"})
fig.update_layout(height=max(350, 32 * n))
st.plotly_chart(fig, width="stretch")

st.subheader("Pareto: how concentrated is revenue?")
st.caption("The line shows cumulative share of total revenue. A steep curve means a few categories drive most sales.")
allc = fetch("top_products", limit=100, **f)
fig = go.Figure()
fig.add_bar(x=allc.category, y=allc.revenue_share_pct, name="Share of revenue (%)")
fig.add_scatter(x=allc.category, y=allc.cumulative_share_pct, name="Cumulative (%)", yaxis="y2", mode="lines+markers")
fig.update_layout(yaxis2=dict(overlaying="y", side="right", range=[0, 105]), height=420,
                  legend=dict(orientation="h", y=1.12))
st.plotly_chart(fig, width="stretch")

st.dataframe(df, width="stretch", hide_index=True)
