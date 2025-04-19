import polars as pl
from datetime import datetime, timedelta
import random


grades = [
    {"name": "Forcados", "group": "medium"},
    {"name": "Bonny Light", "group": "light"},
    {"name": "Qua Iboe", "group": "light"},
    {"name": "Escravos", "group": "medium"},
    {"name": "Bonga", "group": "medium"},
    {"name": "EA", "group": "light"},
    {"name": "Rabi Blend", "group": "heavy"},
    {"name": "Agbami", "group": "heavy"},
    {"name": "Murban", "group": "light"},
    {"name": "WTI", "group": "medium"},
    {"name": "Oriente", "group": "heavy"},
]
incoterms = ["FOB", "CIF", "DAP"]
equity_owners = ["Shell", "Chevron", "Exxon", "Total", "Agip", "NNPC"]
buyers = sellers = [
    "Vitol",
    "BP",
    "Trafigura",
    "Glencore",
    "Unipec",
    "PetroChina",
    "ENOC",
    "Mercuria",
    "Litasco",
    "Gunvor",
    "P66",
    "Other",
]


# Generate random trades
num_trades = 25
base_date = datetime(2025, 4, 1)


def random_date():
    return base_date + timedelta(days=random.randint(0, 60))


def generate_trades(num_trades: int):
    data = []
    for _ in range(num_trades):
        grade = random.choice(grades)["name"]
        group = [g for g in grades if g["name"] == grade][0]["group"]
        incoterm = random.choice(incoterms)
        equity = random.choice(equity_owners)
        seller = random.choice(sellers)
        buyer = random.choice(buyers)
        trade_date = random_date()
        loading_start = trade_date + timedelta(days=random.randint(20, 45))
        loading_end = loading_start + timedelta(days=5)
        pricing = round(random.randint(-300, 600) / 100, 1)
        volume_kbbl = random.choice([650, 950, 1000, 1050])

        data.append(
            {
                "grade": grade,
                "group": group,
                "incoterm": incoterm,
                "equity_owner": equity,
                "seller": seller,
                "buyer": buyer,
                "trade_date": trade_date.date(),
                "loading_start": loading_start.date(),
                "loading_end": loading_end.date(),
                "price_basis": pricing,
                "volume_kbbl": volume_kbbl,
            }
        )

    return pl.DataFrame(data).with_columns(
        [
            (
                pl.col("loading_start").dt.truncate("2w").dt.to_string()
                + " to "
                + (pl.col("loading_start") + pl.duration(days=7))
                .dt.truncate("1w")
                .dt.to_string()
            ).alias("loading_bucket")
        ]
    )
