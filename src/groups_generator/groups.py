import random
from pathlib import Path
from src.config.config import (
    payment_system_coefficients,
    bank_coefficients,
    group_size_coefficients
)

import pandas as pd

from src.card_generator.card import generate_card


PROJECT_DIR = Path(__file__).resolve().parent.parent.parent


df_names = pd.read_parquet(
    PROJECT_DIR / "russian_names.parquet"
)

df_passports = pd.read_parquet(
    PROJECT_DIR / "passports.parquet"
)


df_combined = pd.concat(
    [
        df_names.reset_index(drop=True),
        df_passports.reset_index(drop=True)
    ],
    axis=1
)



group_ids = []

current_id = 0
i = 0
n = len(df_combined)

while i < n:

    size = random.choices(list(group_size_coefficients.keys()),weights=list(group_size_coefficients.values()),k=1)[0]

    size = min(size, n - i)

    group_ids.extend(
        [current_id] * size
    )

    current_id += 1
    i += size


df_combined["Группа"] = group_ids


group_cards = {
    group_id: generate_card(
        payment_system_coefficients,
        bank_coefficients
    )
    for group_id in df_combined["Группа"].unique()
}

df_combined["Номер карты"] = (
    df_combined["Группа"].map(group_cards)
)


df_combined.to_parquet(PROJECT_DIR / "groups.parquet",index=False)
