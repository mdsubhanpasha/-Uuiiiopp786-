"""
Data Profiling and Quality Assessment Engine Module.

Required Functions:
- df.head()
- df.tail()
- df.info()
- df.describe()
- df.shape
- df.dtypes
- df.sample()

Logic: Live profiling, return quality metrics dict.
"""

import io
from typing import Any, Dict
import pandas as pd


def assess_dataframe_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Executes live data profiling and quality metrics extraction using pandas inspection functions.
    """
    head_sample = df.head(5)
    tail_sample = df.tail(5)

    # Capture df.info() string output
    buffer = io.StringIO()
    df.info(buf=buffer)
    info_str = buffer.getvalue()

    describe_stats = df.describe(include="all")
    shape_dim = df.shape
    dtypes_series = df.dtypes
    random_sample = df.sample(n=min(3, len(df))) if not df.empty else df

    metrics = {
        "shape": shape_dim,
        "dtypes": dtypes_series.to_dict(),
        "head": head_sample,
        "tail": tail_sample,
        "sample": random_sample,
        "info_summary": info_str,
        "describe": describe_stats,
        "missing_count": int(df.isna().sum().sum()),
        "duplicate_count": int(df.duplicated().sum())
    }
    return metrics
