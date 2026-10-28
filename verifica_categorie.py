import pandas as pd

df = pd.read_csv("tiktok_ready_posts.csv")
report = df.groupby(["Categoria", "Fascia Prezzo"]).size().unstack(fill_value=0)
print(report)