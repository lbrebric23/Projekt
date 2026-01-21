from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parents[1]          
DATA_PATH = BASE_DIR / "data" / "processed" / "integrated_fashion_data.csv"
OUT_DIR = BASE_DIR / "static"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def load_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Ne postoji CSV: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    return df

def plot_category_scatter(df: pd.DataFrame):
    needed = {"masterCategory", "avg_price", "avg_rating"}
    missing = needed - set(df.columns)
    if missing:
        raise ValueError(f"Fale stupci u CSV-u: {missing}")

    plt.figure()
    plt.scatter(df["avg_price"], df["avg_rating"])

    for _, row in df.iterrows():
        plt.annotate(str(row["masterCategory"]), (row["avg_price"], row["avg_rating"]))

    plt.xlabel("Prosječna cijena")
    plt.ylabel("Prosječna ocjena")
    plt.title("Odnos cijene i ocjene po kategoriji")
    out = OUT_DIR / "scatter_category_price_rating.png"
    plt.savefig(out, bbox_inches="tight")
    plt.close()
    print("Spremljen graf:", out)

def plot_product_ratings(df_products: pd.DataFrame):
    """
    Ovo radi ako imaš DF na razini proizvoda (npr. iz DummyJSON),
    sa stupcima: title, rating, price, category.
    Ako u integriranom CSV-u nema pojedinačnih proizvoda, ovo neće imati smisla
    (jer imaš samo agregate po kategoriji).
    """
    needed = {"title", "rating"}
    if not needed.issubset(df_products.columns):
        print("Preskačem product rating graf (nema title/rating u podacima).")
        return

    top = df_products.sort_values("rating", ascending=False).head(15)

    plt.figure()
    plt.barh(top["title"], top["rating"])
    plt.xlabel("Ocjena")
    plt.ylabel("Proizvod")
    plt.title("Top proizvodi po ocjeni (DummyJSON)")
    out = OUT_DIR / "top_products_by_rating.png"
    plt.savefig(out, bbox_inches="tight")
    plt.close()
    print("Spremljen graf:", out)

def main():
    df = load_data()
    print("Učitano redaka:", len(df))
    print("Stupci:", list(df.columns))

    plot_category_scatter(df)

    raw_dummy = BASE_DIR / "data" / "raw" / "dummyjson_fashion_products.csv"
    if raw_dummy.exists():
        df_dummy = pd.read_csv(raw_dummy)
        plot_product_ratings(df_dummy)
    else:
        print("Nema raw dummy CSV-a za product graf:", raw_dummy)

if __name__ == "__main__":
    main()
