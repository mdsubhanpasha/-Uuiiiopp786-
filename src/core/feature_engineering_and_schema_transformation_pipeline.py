"""
Feature Engineering and Schema Transformation Pipeline Module.

Required Functions:
- df.assign()
- df.rename()
- df.astype()
- Series.map()
- df.apply()
- df.transform()
- df.pipe()

Logic: assign pnl, rename, astype float, map symbol, apply signal, transform normalize, pipe chain.
"""

from typing import Dict
import pandas as pd


def _calculate_pnl(df: pd.DataFrame) -> pd.DataFrame:
    """Internal pipe step to assign PnL calculation."""
    if "current_price" in df.columns:
        return df.assign(pnl_estimate=df["current_price"] * 0.05)
    elif "close" in df.columns and "open" in df.columns:
        return df.assign(pnl_estimate=df["close"] - df["open"])
    return df.assign(pnl_estimate=0.0)


def _apply_trading_signal(row: pd.Series) -> str:
    """Row-level apply callback function."""
    val = row.get("price_change_percentage_24h", row.get("pnl_estimate", 0.0))
    if val > 2.0:
        return "BULLISH_STRONG"
    elif val > 0:
        return "BULLISH"
    elif val < -2.0:
        return "BEARISH_STRONG"
    else:
        return "NEUTRAL"


def execute_feature_engineering_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """
    Executes schema conversion, feature generation, row-wise transformations, and normalization.
    """
    # 1. df.rename(): Rename columns to standard enterprise telemetry schema
    renamed_df = df.rename(columns={
        "Name": "asset_name",
        "symbol": "ticker_symbol",
        "current_price": "unit_price",
        "total_volume": "trade_volume"
    })

    # 2. df.astype(): Enforce standard numeric float64 / string dtypes
    typed_df = renamed_df.copy()
    numeric_targets = ["unit_price", "trade_volume", "open", "high", "low", "close", "pnl_estimate"]
    for col in numeric_targets:
        if col in typed_df.columns:
            typed_df[col] = typed_df[col].astype("float64")

    # 3. Series.map(): Map ticker symbol to currency prefix or sector
    if "ticker_symbol" in typed_df.columns:
        symbol_map = {"btc": "CRYPTO_BTC", "eth": "CRYPTO_ETH", "sol": "CRYPTO_SOL", "ada": "CRYPTO_ADA", "doge": "CRYPTO_DOGE"}
        typed_df["asset_category"] = typed_df["ticker_symbol"].map(lambda x: symbol_map.get(str(x).lower(), f"ASSET_{str(x).upper()}"))
    else:
        typed_df["asset_category"] = "GENERAL"

    # 4. df.assign(): Calculate PnL and return spread
    assigned_df = typed_df.assign(
        volatility_spread=lambda x: (x["high"] - x["low"]) if ("high" in x.columns and "low" in x.columns) else 0.0
    )

    # 5. df.apply(): Apply row-level signal scoring
    assigned_df["trading_signal"] = assigned_df.apply(_apply_trading_signal, axis=1)

    # 6. df.transform(): Z-score normalization transform across numeric attributes
    numeric_cols = assigned_df.select_dtypes(include=["float64", "int64"]).columns
    if len(numeric_cols) > 0:
        z_scores = assigned_df[numeric_cols].transform(lambda x: (x - x.mean()) / (x.std() + 1e-9))
        for col in numeric_cols:
            assigned_df[f"{col}_zscore"] = z_scores[col]

    # 7. df.pipe(): Pipeline method chaining step
    piped_df = assigned_df.pipe(_calculate_pnl)

    return piped_df
