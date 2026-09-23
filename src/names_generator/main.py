from russian_names import RussianNames
import pandas as pd

COUNT = 50

generator = RussianNames(count=COUNT)
people = generator.get_batch()  # список строк "Имя Отчество Фамилия"

split_names = [p.split() for p in people]

df = pd.DataFrame(split_names, columns=["Имя", "Отчество", "Фамилия"])

df.insert(0, "Номер", range(1, len(df) + 1))
df = df[["Номер", "Фамилия", "Имя", "Отчество"]]

#df.to_csv("russian_names.csv", index=False, encoding="utf-8-sig")
df.to_parquet("russian_names.parquet", index=False)

print(f"\nГотово! Сгенерировано {len(df)} записей.")
print(df.head())
