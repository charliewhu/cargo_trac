import typing as t
import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta, date
import polars as pl
import streamlit as st

BASE_DATE = datetime(2025, 6, 1)

grades = [
    {"grade": "Forcados", "group": "medium"},
    {"grade": "Bonny Light", "group": "light"},
    {"grade": "Qua Iboe", "group": "light"},
    {"grade": "Escravos", "group": "medium"},
    {"grade": "Bonga", "group": "medium"},
    {"grade": "EA", "group": "light"},
    {"grade": "Rabi Blend", "group": "heavy"},
    {"grade": "Agbami", "group": "heavy"},
    {"grade": "Murban", "group": "light"},
    {"grade": "WTI", "group": "medium"},
    {"grade": "Oriente", "group": "heavy"},
]
incoterms = ["FOB", "CIF", "DAP"]
counterparties = [
    "Shell",
    "Chevron",
    "Exxon",
    "Total",
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


def create_random_date(base_date=BASE_DATE):
    return (base_date + timedelta(days=random.randint(0, 60))).date()


def create_random_volume():
    return random.choice([650, 950, 1000, 1050])


def get_random_grade():
    return random.choice(grades)


def create_counterparty(name: t.Optional[str] = None):
    return random.choice(counterparties)


@dataclass(unsafe_hash=True)
class Cargo:
    grade: dict = field(default_factory=get_random_grade)
    equity_holder: str = field(default_factory=create_counterparty)
    bl_date: date = field(default_factory=create_random_date)
    volume_kbbl: int = field(default_factory=create_random_volume)


@dataclass(unsafe_hash=True)
class Trade:
    cargo: Cargo
    order_in_chain: int
    struck_date: date
    seller: str = field(default_factory=create_counterparty)
    buyer: str = field(default_factory=create_counterparty)
    incoterm: t.Literal["FOB", "CIF", "DAP"] = field(
        default_factory=lambda: random.choice(incoterms)
    )  # type: ignore
    pricing: float = field(
        default_factory=lambda: round(random.randint(-300, 600) / 100, 1)
    )


def create_trade_chain_for_cargo(cargo: Cargo, chain_length: int) -> list[Trade]:
    """
    For a given Cargo, we must create a Trade chain of length chain_length.
    The trades cannot be between the same Counterparty and the last Buyer must be the
    current Seller (since they own the Cargo at that point).
    The struck_date must also move forward in time.
    """

    trades = []
    current_seller = cargo.equity_holder  # First seller is equity holder
    trade_date = cargo.bl_date + timedelta(days=random.randint(-60, -40))
    diff = round(random.randint(-300, 600) / 100, 1)

    for i in range(chain_length):
        # Avoid self-selling
        possible_buyers = [name for name in counterparties if name != current_seller]
        buyer_name = random.choice(possible_buyers)
        current_buyer = create_counterparty(buyer_name)

        trade = Trade(
            cargo=cargo,
            order_in_chain=i + 1,
            struck_date=trade_date,
            seller=current_seller,
            buyer=current_buyer,
            pricing=diff,
        )
        trades.append(trade)
        current_seller = current_buyer  # Ownership passes on
        trade_date += timedelta(days=random.randint(1, 5))  # increment
        diff += round(random.randint(-50, 50) / 100, 1)

    return trades


@st.cache_data
def create_cargos_and_trade_chains(num_cargos: int = 75, max_trades_per_cargo: int = 5):
    """
    Create a list of Cargos and create trade chains for each.
    """

    cargos = [Cargo() for _ in range(num_cargos)]
    trades: list[Trade] = []

    for cargo in cargos:
        chain_length = random.randint(1, max_trades_per_cargo)
        trades.extend(create_trade_chain_for_cargo(cargo, chain_length))

    # Unnest the Cargo instance to make 'wide' table
    df = (
        pl.DataFrame(trades)
        .unnest("cargo")
        .unnest("grade")
        .with_columns(
            (
                pl.col("bl_date").dt.truncate("2w").dt.to_string()
                + " to "
                + (pl.col("bl_date") + pl.duration(days=14))
                .dt.truncate("2w")
                .dt.to_string()
            ).alias("loading_bucket"),
            pl.col("struck_date").dt.to_string(),
            pl.col("bl_date").dt.to_string(),
        )
    )

    return df
