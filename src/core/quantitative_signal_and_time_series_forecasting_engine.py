"""
Quantitative Signal and Time Series Forecasting Engine Module.

Required Functions:
- pd.to_datetime()
- pd.date_range()
- df.resample()
- df.rolling()
- df.expanding()
- df.shift()
- df.pct_change()

Logic: to_datetime, date_range calendar, resample 1H OHLC, rolling 20 MA, expanding max, shift prev close, pct_change returns.
"""

from typing import Dict
import pandas as pd


def generate_quantitative_signals(stocks_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Computes time-series quantitative indicators, moving averages, pct returns, and rolling windows.
    """
    results = {}

    df = stocks_df.copy()

    # 1. pd.to_datetime(): Parse date strings to DatetimeIndex
    if "date" in df.columns:
        df["datetime"] = pd.to_datetime(df["date"])
    else:
        df["datetime"] = pd.date_range(start="2023-01-01", periods=len(df), freq="D")

    # 2. pd.date_range(): Generate calendar frequency index
    calendar_range = pd.date_range(start="2023-01-01", end="2023-01-31", freq="D")
    results["calendar_index"] = pd.DataFrame({"calendar_date": calendar_range})

    # Work on time-indexed DataFrame for resampling
    ts_df = df.set_index("datetime").sort_index()
    val_col = "close" if "close" in ts_df.columns else ts_df.select_dtypes(include=["number"]).columns[0]

    # 3. df.resample(): Resample tick data to daily/hourly OHLC
    resampled_df = ts_df[val_col].resample("D").ohlc()
    results["resampled_ohlc"] = resampled_df

    # 4. df.pct_change(): Calculate daily return percentage
    ts_df["price_returns"] = ts_df[val_col].pct_change()

    # 5. df.shift(): Shift values to get previous close price
    ts_df["prev_close"] = ts_df[val_col].shift(1)

    # 6. df.rolling(): Moving average and volatility calculation (e.g., 20 MA / window size 3)
    window_sz = min(3, max(1, len(ts_df)))
    ts_df["rolling_mean_ma3"] = ts_df[val_col].rolling(window=window_sz, min_periods=1).mean()
    ts_df["rolling_std"] = ts_df[val_col].rolling(window=window_sz, min_periods=1).std()

    # 7. df.expanding(): Cumulative max and cumulative mean indicator
    ts_df["expanding_max"] = ts_df[val_col].expanding(min_periods=1).max()
    ts_df["expanding_mean"] = ts_df[val_col].expanding(min_periods=1).mean()

    results["signal_features"] = ts_df.reset_index()

    return results
