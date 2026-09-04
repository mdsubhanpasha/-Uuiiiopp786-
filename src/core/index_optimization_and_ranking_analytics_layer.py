"""
Index Optimization and Ranking Analytics Layer Module.

Required Functions:
- df.sort_values()
- df.sort_index()
- df.set_index()
- df.reset_index()
- df.reindex()
- df.nlargest()
- df.nsmallest()

Logic: set_index timestamp, sort_values volume, nlargest gainers, nsmallest losers, reindex date_range.
"""

from typing import Dict
import pandas as pd


def optimize_index_and_rank_assets(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Applies multi-axis index alignment, sorting, custom reindexing, and rank extraction.
    """
    results = {}

    # Target volume or price column for sorting/ranking
    val_col = "total_volume" if "total_volume" in df.columns else ("volume" if "volume" in df.columns else df.select_dtypes(include=["number"]).columns[0])

    # 1. df.sort_values(): Sort by trading volume descending
    sorted_val = df.sort_values(by=val_col, ascending=False)
    results["sorted_by_volume"] = sorted_val

    # 2. df.set_index(): Set custom primary key / index
    if "id" in df.columns:
        indexed_df = df.set_index("id")
    elif "date" in df.columns:
        indexed_df = df.set_index("date")
    else:
        indexed_df = df.set_index(df.columns[0])
    results["indexed"] = indexed_df

    # 3. df.sort_index(): Sort alphabetically or chronologically by index
    sorted_idx = indexed_df.sort_index()
    results["sorted_index"] = sorted_idx

    # 4. df.reset_index(): Reset index back to integer range
    reset_df = sorted_idx.reset_index()
    results["reset_index"] = reset_df

    # 5. df.nlargest() & 6. df.nsmallest(): Top gainers / bottom losers
    n_top = min(5, len(df))
    n_largest = df.nlargest(n_top, columns=val_col)
    n_smallest = df.nsmallest(n_top, columns=val_col)
    results["nlargest"] = n_largest
    results["nsmallest"] = n_smallest

    # 7. df.reindex(): Custom reindexing with calendar date range or new row labels
    new_index = ["bitcoin", "ethereum", "solana", "cardano", "dogecoin", "ripple", "polkadot"]
    if "id" in df.columns:
        reindexed_df = indexed_df.reindex(new_index, fill_value=0)
    else:
        reindexed_df = df.reindex(range(len(df) + 3), fill_value=0)
    results["reindexed"] = reindexed_df

    return results
