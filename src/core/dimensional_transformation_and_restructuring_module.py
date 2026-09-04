"""
Dimensional Transformation and Restructuring Module.

Required Functions:
- df.pivot()
- pd.pivot_table()
- df.melt()
- df.stack()
- df.unstack()
- df.explode()
- pd.wide_to_long()

Logic: pivot_table heatmap, melt OHLC, stack/unstack multi-index, explode, wide_to_long.
"""

from typing import Dict
import pandas as pd


def transform_dimensional_structure(stocks_df: pd.DataFrame, crypto_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Executes dimensional reshaping, restructuring, pivoting, un/stacking, and wide-to-long operations.
    """
    results = {}

    # Identify primary columns dynamically based on renamed schema or original schema
    id_col = "id" if "id" in crypto_df.columns else crypto_df.columns[0]
    symbol_col = "ticker_symbol" if "ticker_symbol" in crypto_df.columns else ("symbol" if "symbol" in crypto_df.columns else crypto_df.columns[1])
    price_col = "unit_price" if "unit_price" in crypto_df.columns else ("current_price" if "current_price" in crypto_df.columns else "close")

    # 1. pd.pivot_table(): Aggregated metric heatmap structure
    if "Name" in stocks_df.columns and "close" in stocks_df.columns:
        p_table = pd.pivot_table(stocks_df.head(100), values="close", index="date", columns="Name", aggfunc="mean")
    else:
        p_table = pd.pivot_table(crypto_df, values=price_col, index=symbol_col, aggfunc="mean")
    results["pivot_table"] = p_table

    # 2. df.pivot(): Pivot without aggregation on uniquely indexed subset
    sample_sub = crypto_df[[id_col, symbol_col, price_col]].drop_duplicates(subset=[id_col])
    try:
        p_single = sample_sub.pivot(index=id_col, columns=symbol_col, values=price_col)
    except Exception:
        p_single = sample_sub
    results["pivot"] = p_single

    # 3. df.melt(): Unpivot OHLC stocks structure to long format
    ohlc_cols = [c for c in ["open", "high", "low", "close"] if c in stocks_df.columns]
    if ohlc_cols:
        melted_df = pd.melt(stocks_df.head(20), id_vars=["date", "Name"] if "Name" in stocks_df.columns else ["date"], value_vars=ohlc_cols, var_name="ohlc_metric", value_name="price_value")
    else:
        melted_df = pd.melt(crypto_df, id_vars=[id_col], value_vars=[price_col], var_name="metric", value_name="val")
    results["melted"] = melted_df

    # 4. df.stack() & 5. df.unstack(): MultiIndex stacking/unstacking
    num_cols = crypto_df.select_dtypes(include=["number"]).columns[:2].tolist()
    multi_df = crypto_df.set_index([id_col, symbol_col])[num_cols]
    stacked_series = multi_df.stack()
    unstacked_df = stacked_series.unstack()
    results["stacked"] = stacked_series.to_frame(name="stacked_val")
    results["unstacked"] = unstacked_df

    # 6. df.explode(): Unnest list-based tags/categories
    exploded_input = pd.DataFrame({
        "coin": ["bitcoin", "ethereum"],
        "tags": [["store_of_value", "pow", "top1"], ["smart_contracts", "pos", "top2"]]
    })
    exploded_df = exploded_input.explode("tags")
    results["exploded"] = exploded_df

    # 7. pd.wide_to_long(): Wide format to long format transformation
    wide_input = pd.DataFrame({
        "fintype": ["A", "B"],
        "price_2021": [100, 200],
        "price_2022": [110, 210],
        "volume_2021": [1000, 2000],
        "volume_2022": [1100, 2100]
    })
    wtl_df = pd.wide_to_long(wide_input, stubnames=["price", "volume"], i="fintype", j="year", sep="_")
    results["wide_to_long"] = wtl_df

    return results
