import random
from pathlib import Path
#from src.config.config import ()

import pandas as pd



path = Path(__file__).parent / "towns.parquet"

df_towns = pd.read_parquet(path)

print(df_towns)