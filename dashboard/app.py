"""Overview page (entry point).  Run:  streamlit run dashboard/app.py"""
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots
from utils import brl, fetch, num, setup

f = setup("Overview", "📊")
st.title("📊 Product Analytics Dashboard")
st.caption("E-commerce performance on the Olist dataset · use the sidebar to filter · other pages are in the sidebar menu")

k = fetch("kpis", **f).iloc[0]
monthly = fetch("revenue_monthly", **f)
if monthly.empty or k.orders == 0:
    st.warning("No delivered orders match these filters.")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Revenue", brl(k.revenue))
c2.metric("Orders", num(k.orders))
c3.metric("Customers", num(k.customers))
c4.metric("Avg. order value", f"R$ {k.aov:,.2f}")

st.subheader("Revenue and orders over time")
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_bar(x=monthly.month, y=monthly.revenue, name="Revenue (R$)", marker_color="#4C78A8")
fig.add_scatter(x=monthly.month, y=monthly.orders, name="Orders", mode="lines+markers",
                line=dict(color="#F58518"), secondary_y=True)
fig.update_yaxes(title_text="Revenue (R$)", secondary_y=False)
fig.update_yaxes(title_text="Orders", secondary_y=True)
fig.update_layout(height=420, legend=dict(orientation="h", y=1.1), margin=dict(t=30))
st.plotly_chart(fig, width="stretch")

left, right = st.columns(2)
with left:
    st.subheader("Top 5 categories")
    top = fetch("top_products", limit=5, **f)
    fig = go.Figure(go.Bar(x=top.revenue[::-1], y=top.category[::-1], orientation="h", marker_color="#54A24B"))
    fig.update_layout(height=320, margin=dict(t=10), xaxis_title="Revenue (R$)")
    st.plotly_chart(fig, width="stretch")
with right:
    st.subheader("Top 5 states")
    geo = fetch("geography", **f).head(5)
    fig = go.Figure(go.Bar(x=geo.revenue[::-1], y=geo.state[::-1], orientation="h", marker_color="#B279A2"))
    fig.update_layout(height=320, margin=dict(t=10), xaxis_title="Revenue (R$)")
    st.plotly_chart(fig, width="stretch")
