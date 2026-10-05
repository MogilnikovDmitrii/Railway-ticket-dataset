from pathlib import Path

import numpy as np
import pandas as pd
from src.config.config import (
    CARRIAGE_TYPES,
    HIGH_SPEED_ROUTE,
    RANDOM_SEED,
    SEASONAL_PERIODS,
    TRAIN_COMPOSITIONS,
    TRAIN_TYPES,
)


BASE_DIR = Path(__file__).parent


def train_number_pairs() -> list[dict]:
    pairs = []
    for train_type, service, first, last, speed in TRAIN_TYPES:
        for odd_number in range(first, last, 2):
            pairs.append({
                "Нечетный номер": odd_number,
                "Четный номер": odd_number + 1,
                "Тип поезда": train_type,
                "Курсирование": service,
                "Маршрутная скорость": speed,
            })
    return pairs


def is_high_speed_route(route_key: tuple[str, str]) -> bool:
    return frozenset(route_key) == HIGH_SPEED_ROUTE


def train_rows(
    routes: pd.DataFrame,
    numbers: dict,
    period: dict,
) -> list[dict]:
    if len(routes) != 2:
        raise ValueError("Для каждого маршрута должны быть записи туда и обратно")

    rows = []
    for _, route in routes.iterrows():
        number = (
            numbers["Четный номер"]
            if route["Направление"] in {"N", "E"}
            else numbers["Нечетный номер"]
        )
        rows.append({
            "Номер поезда": f"{number:03d}",
            "Город отправления": route["Город отправления"],
            "Город назначения": route["Город назначения"],
            "Расстояние": route["Расстояние"],
            "Направление": route["Направление"],
            "Тип поезда": numbers["Тип поезда"],
            "Курсирование": numbers["Курсирование"],
            "Период курсирования": period["Период курсирования"],
            "Месяц начала": period["Месяц начала"],
            "День начала": period["День начала"],
            "Месяц окончания": period["Месяц окончания"],
            "День окончания": period["День окончания"],
            "Маршрутная скорость": numbers["Маршрутная скорость"],
            "Время в пути": round(
                travel_time_hours(route["Расстояние"], numbers["Маршрутная скорость"]),
                2,
            ),
            "Время в пути (ч)": travel_time_text(
                travel_time_hours(route["Расстояние"], numbers["Маршрутная скорость"])
            ),
            "Вместимость поезда": train_capacity(numbers["Тип поезда"]),
        })
    return rows


def train_capacity(train_type: str) -> int:
    return sum(
        count * CARRIAGE_TYPES[code][1]
        for code, count in TRAIN_COMPOSITIONS[train_type].items()
    )


def travel_time_hours(distance: float, speed: float) -> float:
    minutes = round(distance / speed * 60 / 5) * 5
    return round(minutes / 60, 2)


def travel_time_text(hours: float) -> str:
    return f"{hours:.2f}".rstrip("0").rstrip(".") + " ч"


def service_period(service: str, rng: np.random.Generator) -> dict:
    if service == "Круглый год":
        return {
            "Период курсирования": "Круглый год",
            "Месяц начала": 1,
            "День начала": 1,
            "Месяц окончания": 12,
            "День окончания": 31,
        }

    period = SEASONAL_PERIODS[rng.integers(len(SEASONAL_PERIODS))]
    name, start_month, start_day, end_month, end_day = period
    return {
        "Период курсирования": name,
        "Месяц начала": int(start_month),
        "День начала": int(start_day),
        "Месяц окончания": int(end_month),
        "День окончания": int(end_day),
    }


ways = pd.read_parquet(BASE_DIR / "ways.parquet")

ways["_route_key"] = ways.apply(
    lambda row: tuple(sorted((row["Город отправления"], row["Город назначения"]))),
    axis=1,
)
route_pairs = list(ways.groupby("_route_key", sort=False))
high_speed_routes = [pair for pair in route_pairs if is_high_speed_route(pair[0])]
other_routes = [pair for pair in route_pairs if not is_high_speed_route(pair[0])]
number_pairs = train_number_pairs()
high_speed_numbers = [
    pair for pair in number_pairs if pair["Тип поезда"] == "Высокоскоростной"
]
other_numbers = [
    pair for pair in number_pairs if pair["Тип поезда"] != "Высокоскоростной"
]

if len(high_speed_routes) > len(high_speed_numbers):
    raise ValueError(
        "Для высокоскоростных маршрутов не хватает уникальных пар номеров"
    )
if len(other_routes) > len(other_numbers):
    raise ValueError("Для обычных маршрутов не хватает уникальных пар номеров")

rng = np.random.default_rng(RANDOM_SEED)
rng.shuffle(high_speed_numbers)
rng.shuffle(other_numbers)
trains = []

for (_, routes), numbers in zip(high_speed_routes, high_speed_numbers):
    period = service_period(numbers["Курсирование"], rng)
    trains.extend(train_rows(routes, numbers, period))

for (_, routes), numbers in zip(other_routes, other_numbers):
    period = service_period(numbers["Курсирование"], rng)
    trains.extend(train_rows(routes, numbers, period))

pd.DataFrame(trains).to_parquet(BASE_DIR / "trains.parquet", index=False)
