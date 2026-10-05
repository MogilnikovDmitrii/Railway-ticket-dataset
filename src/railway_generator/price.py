from pathlib import Path

import pandas as pd
from src.config.config import (
    CARRIAGE_PRICE_COEFFICIENTS,
    DISTANCE_PRICE_COEFFICIENT,
    TRAIN_BASE_PRICES,
)


BASE_DIR = Path(__file__).parent


def make_prices(seats: pd.DataFrame, flights: pd.DataFrame) -> pd.DataFrame:
    price_by_route = flights.copy()
    price_by_route["Базовая цена"] = price_by_route["Тип поезда"].map(
        TRAIN_BASE_PRICES
    )
    price_by_route["Надбавка за расстояние"] = (
        price_by_route["Расстояние"].astype(float) * DISTANCE_PRICE_COEFFICIENT
    ).round(2)
    price_by_route["Цена билета"] = (
        price_by_route["Базовая цена"] + price_by_route["Надбавка за расстояние"]
    )

    price_columns = [
        "Номер поезда",
        "Дата и время отправления",
        "Тип поезда",
        "Базовая цена",
        "Надбавка за расстояние",
        "Цена билета",
    ]
    carriage_columns = [
        "Номер поезда",
        "Номер вагона",
        "Код вагона",
        "Номер места",
    ]

    prices = seats.merge(
        price_by_route[price_columns],
        on=["Номер поезда", "Дата и время отправления"],
        how="left",
    )
    prices["Коэффициент вагона"] = prices["Код вагона"].map(
        CARRIAGE_PRICE_COEFFICIENTS
    )
    prices["Цена билета"] = (prices["Цена билета"] * prices["Коэффициент вагона"]).round()

    return prices[carriage_columns + [
        "Город отправления",
        "Город назначения",
        "Дата и время отправления",
        "Дата и время прибытия",
        "Тип поезда",
        "Цена билета",
    ]]


seats = pd.read_parquet(BASE_DIR / "seats.parquet")
flights = pd.read_parquet(BASE_DIR / "flights.parquet")
prices = make_prices(seats, flights)
prices.to_parquet(BASE_DIR / "ticket_price.parquet", index=False)
