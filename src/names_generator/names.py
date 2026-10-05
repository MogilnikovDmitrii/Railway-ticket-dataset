from russian_names import RussianNames
import pandas as pd

from src.config.config import COUNT_PASS


generator = RussianNames(count=COUNT_PASS)
people = generator.get_batch()  

split_names = [p.split() for p in people]

df = pd.DataFrame(split_names, columns=["Имя", "Отчество", "Фамилия"])

df.insert(0, "Номер", range(1, len(df) + 1))
df = df[["Номер", "Фамилия", "Имя", "Отчество"]]

df.to_parquet("russian_names.parquet", index=False)
