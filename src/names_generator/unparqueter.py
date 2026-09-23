import pandas as pd

df = pd.read_parquet("russian_names.parquet")

print(df.to_string(index=False))
