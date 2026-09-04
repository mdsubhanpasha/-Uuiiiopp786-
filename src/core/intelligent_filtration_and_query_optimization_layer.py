"""
Intelligent Filtration and Query Optimization Layer Module.

Required Functions:
- df.loc[]
- df.iloc[]
- df.query()
- df.filter()
- df.isin()
- Series.between()
- df.where()

Logic: BTC filter, iloc 100, query >2%, filter like price, isin, between, where masking.
"""

from typing import Dict
import pandas as pd


def apply_intelligent_filtration(crypto_df: pd.DataFrame, stocks_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Applies high-performance filtering, selection, and masking operations using pandas query layer.
    """
    results = {}

    # 1. df.loc[]: BTC filter by symbol or id
    if "symbol" in crypto_df.columns:
        btc_loc = crypto_df.loc[crypto_df["symbol"].str.lower() == "btc"]
    else:
        btc_loc = crypto_df.loc[0:2]
    results["btc_loc"] = btc_loc

    # 2. df.iloc[]: top slice iloc 100 or min available
    iloc_slice = stocks_df.iloc[:min(100, len(stocks_df)), :min(5, len(stocks_df.columns))]
    results["iloc_100"] = iloc_slice

    # 3. df.query(): filter price change or volume > 2% / > 1000
    if "price_change_percentage_24h" in crypto_df.columns:
        query_df = crypto_df.query("price_change_percentage_24h > 0")
    elif "close" in stocks_df.columns:
        query_df = stocks_df.query("close > 100")
    else:
        query_df = crypto_df
    results["query_filtered"] = query_df

    # 4. df.filter(): filter columns like 'price' or 'close'
    filter_df = crypto_df.filter(regex="price|volume|name|symbol")
    results["filter_cols"] = filter_df

    # 5. df.isin(): filter specific target assets
    target_ids = ["bitcoin", "ethereum", "solana", "AAPL", "MSFT"]
    if "id" in crypto_df.columns:
        isin_df = crypto_df[crypto_df["id"].isin(target_ids)]
    elif "Name" in stocks_df.columns:
        isin_df = stocks_df[stocks_df["Name"].isin(target_ids)]
    else:
        isin_df = crypto_df
    results["isin_filtered"] = isin_df

    # 6. Series.between(): range check on numerical values
    if "current_price" in crypto_df.columns:
        between_mask = crypto_df["current_price"].between(10, 500000)
        between_df = crypto_df[between_mask]
    elif "close" in stocks_df.columns:
        between_mask = stocks_df["close"].between(50, 200)
        between_df = stocks_df[between_mask]
    else:
        between_df = crypto_df
    results["between_filtered"] = between_df

    # 7. df.where(): conditional masking for anomaly signals
    numeric_df = crypto_df.select_dtypes(include=["number"])
    where_masked = numeric_df.where(numeric_df > 0, other=0.0)
    results["where_masked"] = where_masked

    return results
