import pandas as pd

df = pd.read_parquet("groups.parquet")
#df = pd.read_parquet("towns.parquet")


print(df.to_string(index=False))
