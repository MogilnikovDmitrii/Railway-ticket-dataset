import pandas as pd

df = pd.read_parquet("groups.parquet")

print(df.to_string(index=False))
