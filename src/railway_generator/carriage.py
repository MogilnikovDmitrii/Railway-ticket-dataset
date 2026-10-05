from pathlib import Path

import pandas as pd
from src.config.config import CARRIAGE_TYPES, TRAIN_COMPOSITIONS


BASE_DIR = Path(__file__).parent

def make_carriages(trains: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for _, train in trains.iterrows():
        train_type = train["Тип поезда"]
        composition = TRAIN_COMPOSITIONS[train_type]
        carriage_number = 1

        for code, count in composition.items():
            description, capacity, compartments = CARRIAGE_TYPES[code]
            for _ in range(count):
                rows.append({
                    "Номер поезда": train["Номер поезда"],
                    "Дата и время отправления": train["Дата и время отправления"],
                    "Дата и время прибытия": train["Дата и время прибытия"],
                    "Город отправления": train["Город отправления"],
                    "Город назначения": train["Город назначения"],
                    "Тип поезда": train_type,
                    "Номер вагона": carriage_number,
                    "Код вагона": code,
                    "Описание": description,
                    "Вместимость вагона": capacity,
                    "Количество купе": compartments,
                })
                carriage_number += 1

    result = pd.DataFrame(rows)
    result["Вместимость поезда"] = result.groupby(
        ["Номер поезда", "Дата и время отправления"]
    )["Вместимость вагона"].transform("sum")
    return result


flights = pd.read_parquet(BASE_DIR / "flights.parquet")
carriages = make_carriages(flights)
carriages.to_parquet(BASE_DIR / "carriages.parquet", index=False)
