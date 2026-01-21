import pandas as pd
import sqlite3

df = pd.read_csv("integrated_fashion_data_v2.csv")

conn = sqlite3.connect("fashion.db")
df.to_sql("category_stats", conn, if_exists="replace", index=False)
conn.close()

print("fashion.db created")
