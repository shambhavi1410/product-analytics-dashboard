import plotly.express as px
import streamlit as st
from utils import fetch, setup

f = setup("Geography", "🗺️")
st.title("🗺️ Sales by State")
df = fetch("geography", **f)
if df.empty:
    st.warning("No data for these filters.")
    st.stop()

st.plotly_chart(px.bar(df, x="state", y="revenue", color="aov", color_continuous_scale="Viridis",
                       labels={"revenue": "Revenue (R$)", "aov": "AOV (R$)"}), width="stretch")
st.subheader("Orders vs average order value")
st.plotly_chart(px.scatter(df, x="orders", y="aov", size="revenue", text="state", log_x=True,
                           labels={"aov": "AOV (R$)", "orders": "Orders (log scale)"}), width="stretch")
st.dataframe(df, width="stretch", hide_index=True)
