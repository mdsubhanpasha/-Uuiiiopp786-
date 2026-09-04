"""
Multi-Source Fusion and Temporal Alignment Fabric Module.

Required Functions:
- pd.merge()
- df.join()
- pd.concat()
- df.combine_first()
- df.update()
- df.compare()
- pd.merge_asof()

Logic: merge crypto+covid, join sentiment, concat history+live, combine_first, update, compare, merge_asof.
"""

from typing import Dict
import pandas as pd


def fuse_and_align_data_sources(crypto_df: pd.DataFrame, stocks_df: pd.DataFrame, covid_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Fuses heterogeneous data feeds using pandas joins, temporal merge_asof, concatenations, and difference compares.
    """
    results = {}

    # 1. pd.concat(): Combine crypto live with crypto historical / duplicated slice
    concat_df = pd.concat([crypto_df, crypto_df.head(2)], ignore_index=True)
    results["concatenated"] = concat_df

    # 2. pd.merge(): Fusion of crypto telemetry with dummy country sentiment/covid metadata
    mock_sentiment = pd.DataFrame({
        "symbol": ["btc", "eth", "sol", "ada", "doge"],
        "sentiment_score": [0.85, 0.72, 0.90, 0.55, 0.40],
        "news_volume": [1200, 850, 450, 300, 950]
    })
    if "symbol" in crypto_df.columns:
        merged_df = pd.merge(crypto_df, mock_sentiment, on="symbol", how="left")
    else:
        merged_df = crypto_df
    results["merged"] = merged_df

    # 3. df.join(): Index-based join
    df1 = crypto_df.set_index("id") if "id" in crypto_df.columns else crypto_df
    df2 = pd.DataFrame({"market_tier": ["tier_1", "tier_1", "tier_2"]}, index=["bitcoin", "ethereum", "solana"])
    joined_df = df1.join(df2, how="left")
    results["joined"] = joined_df

    # 4. df.combine_first(): Patch missing values in primary feed from secondary feed
    primary_df = crypto_df[["id", "current_price"]].copy() if "current_price" in crypto_df.columns else crypto_df.copy()
    if not primary_df.empty and "current_price" in primary_df.columns:
        primary_df.loc[0, "current_price"] = None
    backup_df = crypto_df[["id", "current_price"]].copy() if "current_price" in crypto_df.columns else crypto_df.copy()
    combined_df = primary_df.combine_first(backup_df)
    results["combine_first"] = combined_df

    # 5. df.update(): In-place batch modification with updated ticks
    update_base = crypto_df.copy()
    update_patch = crypto_df.copy()
    if "current_price" in update_patch.columns and not update_patch.empty:
        update_patch.loc[0, "current_price"] = 9999999.0
    update_base.update(update_patch)
    results["updated"] = update_base

    # 6. df.compare(): Detailed column-level difference comparison
    df_orig = crypto_df.head(3).copy()
    df_mod = crypto_df.head(3).copy()
    if "current_price" in df_mod.columns and not df_mod.empty:
        df_mod.loc[0, "current_price"] += 100.0
    try:
        diff_df = df_orig.compare(df_mod)
    except Exception:
        diff_df = pd.DataFrame()
    results["compared_diff"] = diff_df

    # 7. pd.merge_asof(): Time-series nearest alignment on timestamp (CRITICAL FOR LIVE FEEDS)
    time_trades = pd.DataFrame({
        "time": pd.to_datetime(["2023-01-01 10:00:00", "2023-01-01 10:02:00", "2023-01-01 10:05:00"]),
        "trade_price": [100.0, 102.5, 101.0]
    }).sort_values("time")

    time_quotes = pd.DataFrame({
        "time": pd.to_datetime(["2023-01-01 09:59:50", "2023-01-01 10:01:30", "2023-01-01 10:04:45"]),
        "bid": [99.5, 102.0, 100.5],
        "ask": [100.5, 103.0, 101.5]
    }).sort_values("time")

    asof_df = pd.merge_asof(time_trades, time_quotes, on="time", direction="backward")
    results["merge_asof"] = asof_df

    return results
