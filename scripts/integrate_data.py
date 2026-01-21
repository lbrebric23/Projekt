import argparse
from pathlib import Path
import pandas as pd

def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Ne postoji datoteka: {path}")
    return pd.read_csv(path)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-dir", default=".", help="Root folder projekta (default: .)")
    args = parser.parse_args()

    base = Path(args.base_dir).resolve()

    kaggle_path = base / "data" / "processed" / "kaggle_clean.csv"
    dummy_fashion_path = base / "data" / "raw" / "dummyjson_fashion_products.csv"
    dummy_beauty_path = base / "data" / "raw" / "dummyjson_beauty_products.csv"
    out_path = base / "data" / "processed" / "integrated_fashion_data.csv"

    df_kaggle = load_csv(kaggle_path)
    df_fashion = load_csv(dummy_fashion_path)
    df_beauty = load_csv(dummy_beauty_path)

    df_dummy = pd.concat([df_fashion, df_beauty], ignore_index=True)

    df_kaggle["masterCategory"] = df_kaggle["masterCategory"].astype(str).str.lower().str.strip()
    df_dummy["category"] = df_dummy["category"].astype(str).str.lower().str.strip()

    category_mapping = {
        "mens-shirts": "apparel",
        "womens-dresses": "apparel",
        "tops": "apparel",
        "mens-shoes": "footwear",
        "womens-shoes": "footwear",
        "womens-bags": "accessories",
        "sunglasses": "accessories",
        "mens-watches": "accessories",
        "womens-watches": "accessories",

        "beauty": "personal care",
        "fragrances": "personal care",
        "skin-care": "personal care",
    }

    df_dummy["mappedCategory"] = df_dummy["category"].map(category_mapping)

    df_dummy_mapped = df_dummy.dropna(subset=["mappedCategory"]).copy()

    df_dummy_agg = (
        df_dummy_mapped
        .groupby("mappedCategory", as_index=False)
        .agg(
            avg_price=("price", "mean"),
            avg_rating=("rating", "mean"),
            dummy_count=("id", "count"),
        )
    )

    count_col = "id" if "id" in df_kaggle.columns else df_kaggle.columns[0]
    df_kaggle_agg = (
        df_kaggle
        .groupby("masterCategory", as_index=False)
        .agg(kaggle_count=(count_col, "count"))
    )

    df_integrated = pd.merge(
        df_kaggle_agg,
        df_dummy_agg,
        left_on="masterCategory",
        right_on="mappedCategory",
        how="inner"
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    df_integrated.to_csv(out_path, index=False)

    print("Integracija gotova")
    print("Ulazi:")
    print(" -", kaggle_path)
    print(" -", dummy_fashion_path)
    print(" -", dummy_beauty_path)
    print("Izlaz:")
    print(" -", out_path)
    print("\nPreview:")
    print(df_integrated.head(10))

if __name__ == "__main__":
    main()
