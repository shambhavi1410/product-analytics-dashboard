import plotly.express as px
import streamlit as st
from utils import fetch, setup

f = setup("Revenue Trends", "💰")
st.title("💰 Revenue Trends")
monthly = fetch("revenue_monthly", **f)
if monthly.empty:
    st.warning("No data for these filters.")
    st.stop()

a, b = st.columns(2)
with a:
    st.subheader("Average order value (AOV)")
    st.caption("AOV = revenue ÷ orders. Rising AOV means customers are buying more per order.")
    st.plotly_chart(px.line(monthly, x="month", y="aov", markers=True, labels={"aov": "AOV (R$)"}),
                    width="stretch")
with b:
    st.subheader("Month-over-month revenue growth")
    st.caption("% change in revenue versus the previous month.")
    fig = px.bar(monthly, x="month", y="mom_growth_pct", labels={"mom_growth_pct": "MoM growth (%)"},
                 color=monthly.mom_growth_pct.fillna(0) >= 0,
                 color_discrete_map={True: "#54A24B", False: "#E45756"})
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, width="stretch")

st.subheader("Delivery performance and satisfaction")
delivery = fetch("delivery", **f)
a, b, c = st.columns(3)
a.plotly_chart(px.line(delivery, x="month", y="avg_delivery_days", markers=True, title="Avg delivery days"),
               width="stretch")
b.plotly_chart(px.line(delivery, x="month", y="late_pct", markers=True, title="Late deliveries (%)"),
               width="stretch")
c.plotly_chart(px.line(delivery, x="month", y="avg_review_score", markers=True, title="Avg review score (1–5)"),
               width="stretch")

st.subheader("Payment methods")
pay = fetch("payments", **f)
st.plotly_chart(px.pie(pay, names="payment_type", values="payment_value", hole=.45), width="stretch")

with st.expander("See the monthly table"):
    st.dataframe(monthly, width="stretch", hide_index=True)
