import random
import streamlit as st
import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt

from cargo_trac.data import cargos

st.set_page_config(
    page_title="Cargo Trac",
    page_icon=":ship:",
    layout="wide",
)

random.seed(1)

st.title("🛢️ Cargo Trac")

st.subheader("🔥 Trade Heatmap")

trades = cargos.create_cargos_and_trade_chains()
grade_groups = list({g["group"] for g in cargos.grades})
grades = [g["grade"] for g in cargos.grades]

with st.sidebar:
    st.markdown("## Filter")

    counterparties = st.multiselect(
        label="Counterparty",
        options=sorted(cargos.counterparties),
    )

    grade_filter = st.multiselect(
        label="Grade",
        options=sorted(grades),
    )

    group_filter = st.multiselect(
        label="Grade Group",
        options=grade_groups,
    )

    # date = st.date_input(
    #     label="Loading Range",
    #     format="DD/MM/YYYY",
    # )


df = (
    trades.filter(pl.col("buyer").is_in(counterparties or cargos.counterparties))
    .filter(pl.col("group").is_in(group_filter or grade_groups))
    .filter(pl.col("grade").is_in(grade_filter or grades))
)

# Group by grade and loading window
heatmap_df = (
    df.group_by(["group", "loading_bucket"])
    .agg(
        [
            pl.len().alias("num_trades"),
            pl.col("pricing").n_unique().alias("unique_prices"),
            pl.col("volume_kbbl").sum().alias("total_volume"),
        ]
    )
    .sort(["group", "loading_bucket"])
)

# Pivot for heatmap
pivot = heatmap_df.to_pandas().pivot(
    index="group",
    columns="loading_bucket",
    values="num_trades",
)

# Plot heatmap
fig, ax = plt.subplots(figsize=(12, 6))
sns.heatmap(
    pivot,
    ax=ax,
    fmt=".0f",
    cmap="Blues",
    linewidths=3,
    annot=True,
    annot_kws={"fontsize": 12},
)
plt.title("Number of Trades by Grade Group and Loading Window")
plt.xlabel("BL Date Bucket")
plt.ylabel("Grade Group")
fig.autofmt_xdate()
st.pyplot(fig)

# raw data
st.subheader("🔍 Raw Trade Data")
st.dataframe(df.sort("bl_date", "grade", "struck_date"))


# bid/offer board
st.subheader("📈 Bid/Offer Board")
st.text("(Select single grade to view bid/offer chart)")
if len(grade_filter) == 1:
    st.text("Here it is")
