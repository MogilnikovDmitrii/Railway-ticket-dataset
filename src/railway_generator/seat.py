from pathlib import Path

import pandas as pd
from src.config.config import COUNT_PASS

BASE_DIR = Path(__file__).parent


def make_seats(carriages: pd.DataFrame) -> pd.DataFrame:
    rows = []
    flight_columns = [
        "Номер поезда",
        "Дата и время отправления",
        "Дата и время прибытия",
    ]
    seat_generators = []

    for _, flight_carriages in carriages.groupby(flight_columns, sort=False):
        def seats_for_flight(carriages=flight_carriages):
            carriage_generators = []
            for _, carriage in carriages.iterrows():
                def seats_for_carriage(row=carriage):
                    for seat_number in range(1, int(row["Вместимость вагона"]) + 1):
                        yield {
                            "Номер поезда": row["Номер поезда"],
                            "Дата и время отправления": row["Дата и время отправления"],
                            "Дата и время прибытия": row["Дата и время прибытия"],
                            "Город отправления": row["Город отправления"],
                            "Город назначения": row["Город назначения"],
                            "Номер вагона": row["Номер вагона"],
                            "Код вагона": row["Код вагона"],
                            "Номер места": seat_number,
                        }

                carriage_generators.append(iter(seats_for_carriage()))

            while carriage_generators:
                remaining = []
                for seats in carriage_generators:
                    try:
                        yield next(seats)
                        remaining.append(seats)
                    except StopIteration:
                        pass
                carriage_generators = remaining

        seat_generators.append(iter(seats_for_flight()))

    while seat_generators and len(rows) < COUNT_PASS:
        remaining = []
        for seats in seat_generators:
            if len(rows) >= COUNT_PASS:
                break
            try:
                rows.append(next(seats))
                remaining.append(seats)
            except StopIteration:
                pass
        seat_generators = remaining

    return pd.DataFrame(rows)


carriages = pd.read_parquet(BASE_DIR / "carriages.parquet")
seats = make_seats(carriages)
seats.to_parquet(BASE_DIR / "seats.parquet", index=False)
