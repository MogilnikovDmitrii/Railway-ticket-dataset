from pathlib import Path

import pandas as pd
import numpy as np
from src.config.config import (
    FLIGHT_LETTERS,
    MAX_FLIGHTS,
    RANDOM_SEED,
    SCHEDULE_END,
    SCHEDULE_START,
    TURNAROUND_DAYS,
)


BASE_DIR = Path(__file__).parent
TIME_FORMAT = "%Y-%m-%d %H:%M"


def format_time(value: pd.Timestamp) -> str:
    return pd.Timestamp(value).round("min").strftime(TIME_FORMAT)


def travel_time_text(hours: float) -> str:
    return f"{hours:.2f}".rstrip("0").rstrip(".") + " ч"


def period_bounds(train: pd.Series, year: int) -> tuple[pd.Timestamp, pd.Timestamp]:
    start = pd.Timestamp(year=year, month=int(train["Месяц начала"]),
                         day=int(train["День начала"]))
    end = pd.Timestamp(year=year, month=int(train["Месяц окончания"]),
                       day=int(train["День окончания"]), hour=23, minute=59, second=59)
    if end < start:
        end = end + pd.DateOffset(years=1)
    return start, end


def within_period(departure: pd.Timestamp, arrival: pd.Timestamp,
                  start: pd.Timestamp, end: pd.Timestamp) -> bool:
    return start <= departure and arrival <= end


def make_flights(trains: pd.DataFrame) -> pd.DataFrame:
    trains = trains.copy()
    trains["_number"] = pd.to_numeric(trains["Номер поезда"])
    odd_trains = trains[trains["_number"] % 2 == 1]
    even_trains = trains[trains["_number"] % 2 == 0]
    schedule_start = pd.Timestamp(SCHEDULE_START)
    schedule_end = pd.Timestamp(SCHEDULE_END)
    flights = []
    available = list(odd_trains.index)
    next_departure = {}
    rng = odd_trains.sample(frac=1).index.to_list()
    pick = np.random.default_rng(RANDOM_SEED)

    def flight_number(train_number: str) -> str:
        letter = pick.choice(FLIGHT_LETTERS)
        return f"{train_number}{letter}"

    while available:
        odd_index = rng.pop(0)
        if odd_index not in available:
            continue
        available.remove(odd_index)
        odd_train = odd_trains.loc[odd_index]
        even_number = int(odd_train["_number"]) + 1
        reverse = even_trains[even_trains["_number"] == even_number]
        if reverse.empty:
            raise ValueError(f"Не найден обратный поезд для {even_number - 1:03d}")

        reverse = reverse.iloc[0]
        odd_number = int(odd_train["_number"])

        if odd_number in next_departure:
            departure = next_departure[odd_number]
            start, end = period_bounds(odd_train, departure.year)
        else:
            start, end = period_bounds(odd_train, schedule_start.year)
            start = max(start, schedule_start)
            end = min(end, schedule_end)
            window = (end - start).total_seconds() / 3600
            if window <= 0:
                continue
            departure = start + pd.Timedelta(hours=float(pick.integers(0, int(window))))

        if departure < start or departure > end:
            continue

        first_arrival = departure + pd.to_timedelta(
            odd_train["Время в пути"], unit="h"
        )
        reverse_departure = first_arrival + pd.Timedelta(days=TURNAROUND_DAYS)
        reverse_arrival = reverse_departure + pd.to_timedelta(
            reverse["Время в пути"], unit="h"
        )
        if not within_period(departure, reverse_arrival, start, end):
            continue

        flights.extend([
                {
                    "Номер поезда": flight_number(odd_train["Номер поезда"]),
                    "Город отправления": odd_train["Город отправления"],
                    "Город назначения": odd_train["Город назначения"],
                    "Тип поезда": odd_train["Тип поезда"],
                    "Расстояние": odd_train["Расстояние"],
                    "Направление": odd_train["Направление"],
                    "Дата и время отправления": format_time(departure),
                    "Дата и время прибытия": format_time(first_arrival),
                    "Время в пути": travel_time_text(odd_train["Время в пути"]),
                    "Вместимость поезда": odd_train["Вместимость поезда"],
                    "Период курсирования": odd_train["Период курсирования"],
                    "Курсирование": odd_train["Курсирование"],
                    "Месяц начала": odd_train["Месяц начала"],
                    "День начала": odd_train["День начала"],
                    "Месяц окончания": odd_train["Месяц окончания"],
                    "День окончания": odd_train["День окончания"],
                },
                {
                    "Номер поезда": flight_number(reverse["Номер поезда"]),
                    "Город отправления": reverse["Город отправления"],
                    "Город назначения": reverse["Город назначения"],
                    "Тип поезда": reverse["Тип поезда"],
                    "Расстояние": reverse["Расстояние"],
                    "Направление": reverse["Направление"],
                    "Дата и время отправления": format_time(reverse_departure),
                    "Дата и время прибытия": format_time(reverse_arrival),
                    "Время в пути": travel_time_text(reverse["Время в пути"]),
                    "Вместимость поезда": reverse["Вместимость поезда"],
                    "Период курсирования": reverse["Период курсирования"],
                    "Курсирование": reverse["Курсирование"],
                    "Месяц начала": reverse["Месяц начала"],
                    "День начала": reverse["День начала"],
                    "Месяц окончания": reverse["Месяц окончания"],
                    "День окончания": reverse["День окончания"],
                },
        ])
        next_departure[odd_number] = (
            reverse_arrival + pd.Timedelta(days=TURNAROUND_DAYS)
        )

        if next_departure[odd_number] <= end:
            available.append(odd_index)
            rng.append(odd_index)
        if len(flights) >= MAX_FLIGHTS:
            break

    return pd.DataFrame(flights)


trains = pd.read_parquet(BASE_DIR / "trains.parquet")
flights = make_flights(trains)
flights.to_parquet(BASE_DIR / "flights.parquet", index=False)
