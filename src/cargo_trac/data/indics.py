"""
Generate a series of indicative+firm bids/offers for each grade.
There can be multiple per day, per grade.
They must be relatively close in price to each other for realism.
This will be the input for a bid/offer heatmap.
"""

import typing as t
from datetime import timedelta
import random
import polars as pl
from . import dims


def get_indics_for_dates(
    direction: t.Literal["bid", "offer"],
    grade: dict,
    pricing: float,
):
    """
    Loop through dates and generate indics.
    This prevents having equal numbers of bids/offers per day.
    """
    date = dims.BASE_DATE
    max_date = dims.BASE_DATE + timedelta(days=dims.MAX_DAYS)

    indics = []

    while date <= max_date:
        base_indic = {
            "date": date,
            "grade": grade,
            "direction": direction,
        }

        indics.append(
            {
                **base_indic,
                "counterparty": dims.get_random_counterparty(),
                "pricing": round(pricing, 1),
                "type": random.choices(["indic", "firm"], weights=[0.8, 0.2])[0],
            }
        )

        # move date by 0-1 days
        date += timedelta(days=random.choices([0, 1], weights=[0.9, 0.1])[0])

        # add variability to indics
        pricing += round(random.randint(-10, 10) / 100, 1)

    return indics


def generate_indics():
    indics = []

    for grade in dims.grades:
        bid_pricing = round(random.randint(-300, 600) / 100, 1)
        offer_pricing = bid_pricing + round(random.randint(70, 100) / 100, 1)

        bids = get_indics_for_dates(
            direction="bid",
            grade=grade,
            pricing=bid_pricing,
        )
        offers = get_indics_for_dates(
            direction="offer",
            grade=grade,
            pricing=offer_pricing,
        )

        indics.extend(bids + offers)

    indics = pl.DataFrame(indics).unnest("grade")

    return indics
