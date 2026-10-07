import plotly.graph_objects as go
import streamlit as st
from utils import fetch, setup

f = setup("Funnel", "🔻")
st.title("🔻 Order Funnel")
st.caption("Olist has no click-stream data, so this funnel follows the order lifecycle: "
           "a stage counts as reached when its timestamp exists.")
df = fetch("funnel", **f)
if df.empty or df.orders.iloc[0] == 0:
    st.warning("No data for these filters.")
    st.stop()

fig = go.Figure(go.Funnel(y=df.stage, x=df.orders, textinfo="value+percent initial",
                          marker=dict(color=["#4C78A8", "#72B7B2", "#54A24B", "#EECA3B", "#F58518"])))
fig.update_layout(height=450, margin=dict(t=10))
st.plotly_chart(fig, width="stretch")

df["dropped"] = df.orders.shift(1) - df.orders
worst = df.dropna(subset=["dropped"]).sort_values("dropped", ascending=False).iloc[0]
st.info(f"Biggest drop-off: **{worst.stage}** stage — {int(worst.dropped):,} orders lost "
        f"({100 - worst.pct_of_previous:.1f}% of the previous stage).")
st.dataframe(df.rename(columns={"pct_of_start": "% of purchased", "pct_of_previous": "% of previous stage"}),
             width="stretch", hide_index=True)
