import argparse
import os
from pathlib import Path

import pandas as pd
import requests


BASE_URL = "https://dummyjson.com"


FASHION_CATEGORIES = [
    "mens-shirts",
    "mens-shoes",
    "womens-dresses",
    "womens-shoes",
    "sunglasses",
    "womens-bags",
    "mens-watches",
    "womens-watches",
]

BEAUTY_CATEGORIES = [
    "beauty",
    "fragrances",
]


def fetch_json(url: str, params: dict | None = None) -> dict:
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def fetch_all_products() -> pd.DataFrame:
    rows = []
    skip = 0
    limit = 100
    while True:
        data = fetch_json(f"{BASE_URL}/products", params={"limit": limit, "skip": skip})
        products = data.get("products", [])
        if not products:
            break
        rows.extend(products)
        skip += limit
        total = data.get("total", 0)
        if total and skip >= total:
            break

    df = pd.DataFrame(rows)
    keep = ["id", "title", "category", "price", "rating", "brand"]
    df = df[[c for c in keep if c in df.columns]].copy()
    df["category"] = df["category"].astype(str).str.lower().str.strip()
    return df


def fetch_categories(categories: list[str]) -> pd.DataFrame:
    rows = []
    for cat in categories:
        skip = 0
        limit = 100
        while True:
            data = fetch_json(
                f"{BASE_URL}/products/category/{cat}",
                params={"limit": limit, "skip": skip},
            )
            products = data.get("products", [])
            if not products:
                break

            for p in products:
                rows.append(
                    {
                        "id": p.get("id"),
                        "title": p.get("title"),
                        "category": p.get("category"),
                        "price": p.get("price"),
                        "rating": p.get("rating"),
                        "brand": p.get("brand"),
                        "reviews_count": len(p.get("reviews", []) or []),
                    }
                )

            skip += limit
            total = data.get("total", 0)
            if total and skip >= total:
                break

    df = pd.DataFrame(rows)
    if not df.empty:
        df["category"] = df["category"].astype(str).str.lower().str.strip()
    return df


def main():
    parser = argparse.ArgumentParser(
        description="Preuzmi DummyJSON proizvode i spremi CSV u data/ folder."
    )
    parser.add_argument(
        "--outdir",
        default=str(Path(__file__).resolve().parents[1] / "data"),
        help="Folder gdje se spremaju CSV datoteke (default: ./data)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Preuzmi /products i spremi dummyjson_products.csv",
    )
    parser.add_argument(
        "--fashion",
        action="store_true",
        help="Preuzmi fashion kategorije i spremi dummyjson_fashion_products.csv",
    )
    parser.add_argument(
        "--beauty",
        action="store_true",
        help="Preuzmi beauty/fragrances i spremi dummyjson_beauty_products.csv",
    )

    args = parser.parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    if not (args.all or args.fashion or args.beauty):
        args.fashion = True
        args.beauty = True

    if args.all:
        df_all = fetch_all_products()
        out = outdir / "dummyjson_products.csv"
        df_all.to_csv(out, index=False)
        print("Spremljeno:", out)
        print("Broj proizvoda:", len(df_all))

    if args.fashion:
        df_f = fetch_categories(FASHION_CATEGORIES)
        out = outdir / "dummyjson_fashion_products.csv"
        df_f.to_csv(out, index=False)
        print("Spremljeno:", out)
        print("Fashion count:", len(df_f))
        if not df_f.empty:
            print(df_f["category"].value_counts())

    if args.beauty:
        df_b = fetch_categories(BEAUTY_CATEGORIES)
        out = outdir / "dummyjson_beauty_products.csv"
        df_b.to_csv(out, index=False)
        print("Spremljeno:", out)
        print("Beauty count:", len(df_b))
        if not df_b.empty:
            print(df_b["category"].value_counts())


if __name__ == "__main__":
    main()
