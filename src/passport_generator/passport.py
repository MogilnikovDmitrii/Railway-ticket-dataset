import random
import json
import pandas as pd
from pathlib import Path
from src.config.config import COUNT_PASS

BASE_DIR = Path(__file__).resolve().parent

with open(BASE_DIR / "okato_codes.txt", "r", encoding="utf-8") as file:
    okato_codes = json.load(file)

pasports = set()

while len(pasports) < COUNT_PASS:
    series = random.choice(okato_codes) + str((random.randint(97,126))%100).zfill(2)
    number = str(random.randint(100000,999999))

    pasports.add(series+" "+number)



df_passports = pd.DataFrame(list(pasports), columns=["Паспорт"])  
df_passports.to_parquet("passports.parquet", index=False)



