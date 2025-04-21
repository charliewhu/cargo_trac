"""Shared dimensions / reusable data"""

import random
from datetime import datetime, timedelta


BASE_DATE = datetime(2025, 6, 1).date()
MAX_DAYS = 60

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
    return base_date + timedelta(days=random.randint(0, MAX_DAYS))


def create_random_volume():
    return random.choice([650, 950, 1000, 1050])


def get_random_grade():
    return random.choice(grades)


def get_random_counterparty():
    return random.choice(counterparties)
