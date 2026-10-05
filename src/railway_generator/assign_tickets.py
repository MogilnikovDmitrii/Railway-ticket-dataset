from pathlib import Path

import pandas as pd
from src.config.config import RANDOM_SEED


PROJECT_DIR = Path(__file__).resolve().parents[2]
WAY_DIR = Path(__file__).resolve().parent


def assign_tickets(passengers: pd.DataFrame, seats: pd.DataFrame) -> pd.DataFrame:
    if len(seats) < len(passengers):
        raise ValueError(
            f"Пассажиров: {len(passengers)}, доступных мест: {len(seats)}. "
            "Увеличьте COUNT_PASS для мест или уменьшите количество пассажиров."
        )

    assigned_seats = seats.sample(
        n=len(passengers),
        replace=False,
        random_state=RANDOM_SEED,
    ).reset_index(drop=True)
    passengers = passengers.reset_index(drop=True).copy()
    passengers = passengers.drop(columns=["Группа"], errors="ignore")
    assigned_seats = assigned_seats.drop(
        columns=[
            "Расстояние",
            "Базовая цена",
            "Надбавка за расстояние",
            "Коэффициент вагона",
        ],
        errors="ignore",
    )
    return pd.concat([passengers, assigned_seats], axis=1)


passengers = pd.read_parquet(PROJECT_DIR / "groups.parquet")
seats = pd.read_parquet(WAY_DIR / "ticket_price.parquet")
tickets = assign_tickets(passengers, seats)
tickets.to_parquet(PROJECT_DIR / "tickets.parquet", index=False)
tickets.to_csv(PROJECT_DIR / "tickets.csv", index=False, encoding="utf-8-sig")
