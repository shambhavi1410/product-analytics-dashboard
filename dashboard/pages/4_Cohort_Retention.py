import plotly.express as px
import streamlit as st
from utils import fetch, num, setup

setup("Cohort Retention", "🔁")
st.title("🔁 Cohort Retention")
st.caption("Cohort = month of a customer's first purchase. Each cell = % of that cohort who bought again N months later.")

summary = fetch("retention").iloc[0]
a, b, c = st.columns(3)
a.metric("Customers", num(summary.customers))
b.metric("Repeat customers", num(summary.repeat_customers))
c.metric("Repeat-purchase rate", f"{summary.repeat_rate_pct:.2f}%")

df = fetch("cohort")
max_m = st.slider("Months to show", 3, 18, 12)
df = df[df.months_since <= max_m]
pivot = df.pivot(index="cohort_month", columns="months_since", values="retention_pct")
vmax = max(1.0, float(pivot.drop(columns=0).max().max()))  # colour scale ignores the trivial 100% month 0
fig = px.imshow(pivot, text_auto=".1f", aspect="auto", color_continuous_scale="Blues", range_color=(0, vmax),
                labels=dict(x="Months since first purchase", y="Cohort", color="Retention %"))
fig.update_layout(height=max(400, 28 * len(pivot)))
st.plotly_chart(fig, width="stretch")
st.caption("Colour scale is capped so months 1+ are readable (month 0 is always 100%). "
           "Low retention is typical for marketplaces where most customers buy only once.")
