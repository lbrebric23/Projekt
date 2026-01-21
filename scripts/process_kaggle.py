import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
RAW_DATA = os.path.join(BASE_DIR, "data", "raw", "styles.csv")
OUT_DATA = os.path.join(BASE_DIR, "data", "processed", "kaggle_clean.csv")

os.makedirs(os.path.dirname(OUT_DATA), exist_ok=True)

df = pd.read_csv(RAW_DATA, on_bad_lines="skip")
print("Ukupno redaka (original):", len(df))

columns_to_keep = [
    "id", "gender", "masterCategory", "subCategory",
    "articleType", "baseColour", "season", "year", "usage"
]
df = df[columns_to_keep].dropna()

print("Ukupno redaka (očišćeno):", len(df))

df.to_csv(OUT_DATA, index=False)
print("Spremljeno u:", OUT_DATA)
