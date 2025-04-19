import random
import streamlit as st
import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt

from cargo_trac import data

st.set_page_config(
    page_title="Cargo Trac",
    page_icon=":ship:",
    layout="wide",
)

random.seed(1)

# Title
st.title("📊 Crude Oil Trade Heatmap Dashboard")

# Load data (you can replace this with st.file_uploader or path to your CSV)
df = data.generate_trades(50)


# Group by grade and loading window
heatmap_df = (
    df.group_by(["grade", "loading_bucket"])
    .agg(
        [
            pl.len().alias("num_trades"),
            pl.col("price_basis").n_unique().alias("unique_prices"),
            pl.col("volume_kbbl").sum().alias("total_volume"),
        ]
    )
    .sort(["grade", "loading_bucket"])
)

# Pivot for heatmap
df_pandas = heatmap_df.to_pandas()
pivot = df_pandas.pivot(index="grade", columns="loading_bucket", values="num_trades")

# Plot heatmap
fig, ax = plt.subplots(figsize=(12, 6))
sns.heatmap(pivot, annot=True, fmt=".0f", cmap="YlGnBu", linewidths=0.5, ax=ax)
plt.title("Number of Trades by Grade and Loading Window")
plt.xlabel("Loading Window")
plt.ylabel("Crude Grade")
fig.autofmt_xdate()
st.pyplot(fig)


# Expandable section for raw data
with st.expander("🔍 View Raw Trade Data"):
    st.dataframe(df.sort("trade_date").to_pandas())
