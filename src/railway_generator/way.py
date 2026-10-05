from pathlib import Path

import numpy as np
import pandas as pd
from src.config.config import RANDOM_SEED, ROUTE_PAIRS


BASE_DIR = Path(__file__).parent
towns = pd.read_parquet(BASE_DIR / "towns.parquet")

if str(towns.columns[0]).lower() not in {"город", "название", "name", "city"}:
    first_row = pd.DataFrame([towns.columns], columns=towns.columns)
    towns = pd.concat([first_row, towns], ignore_index=True)

towns = towns.iloc[:, [0, 2, 3]].copy()
towns.columns = ["Город", "Широта", "Долгота"]
towns["Широта"] = pd.to_numeric(towns["Широта"])
towns["Долгота"] = pd.to_numeric(towns["Долгота"])

towns["_id"] = np.arange(len(towns))
forward = towns.merge(towns, how="cross", suffixes=(" отправления", " назначения"))
forward = forward[forward["_id отправления"] < forward["_id назначения"]].copy()

if ROUTE_PAIRS > len(forward):
    raise ValueError(
        f"Нельзя выбрать {ROUTE_PAIRS} пар: доступно только {len(forward)}"
    )

forward = forward.sample(
    n=ROUTE_PAIRS,
    random_state=RANDOM_SEED,
).reset_index(drop=True)
backward = forward.copy()
for field in ("Город", "Широта", "Долгота", "_id"):
    backward[[f"{field} отправления", f"{field} назначения"]] = backward[
        [f"{field} назначения", f"{field} отправления"]
    ].to_numpy()
routes = pd.concat([forward, backward], ignore_index=True)

lat_1 = np.radians(routes["Широта отправления"])
lat_2 = np.radians(routes["Широта назначения"])
lon_1 = np.radians(routes["Долгота отправления"])
lon_2 = np.radians(routes["Долгота назначения"])

a = (
    np.sin((lat_2 - lat_1) / 2) ** 2
    + np.cos(lat_1) * np.cos(lat_2) * np.sin((lon_2 - lon_1) / 2) ** 2
)

routes["Расстояние"] = (6371.0088 * 2 * np.arcsin(np.sqrt(a))).round(1) * 1.35

azimuth = np.degrees(np.arctan2(
    np.sin(lon_2 - lon_1) * np.cos(lat_2),
    np.cos(lat_1) * np.sin(lat_2)
    - np.sin(lat_1) * np.cos(lat_2) * np.cos(lon_2 - lon_1),
)) % 360
directions = np.array(["N", "E", "S", "W"])
routes["Направление"] = directions[((azimuth + 45) // 90).astype(int) % 4]

routes[
    ["Город отправления", "Город назначения", "Расстояние", "Направление"]
].to_parquet(BASE_DIR / "ways.parquet", index=False)
