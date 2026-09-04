"""
Distributed Aggregation and Analytical Cube Engine Module.

Required Functions:
- df.groupby()
- groupby.agg()
- groupby.transform()
- Series.value_counts()
- df.nunique()
- groupby.size()
- pd.crosstab()

Logic: groupby coin, agg mean, transform z-score, value_counts signals, nunique, size, crosstab.
"""

from typing import Dict, Any
import pandas as pd


def compute_analytical_cubes(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes distributed multi-dimensional group statistics, contingent cross-tabulations, and cardinality cubes.
    """
    results = {}

    group_col = "name" if "name" in df.columns else ("Name" if "Name" in df.columns else df.columns[0])
    num_cols = df.select_dtypes(include=["number"]).columns.tolist()
    primary_num = num_cols[0] if num_cols else df.columns[1]

    # 1. df.groupby() & 2. groupby.agg(): Multi-metric aggregation
    grouped = df.groupby(group_col)
    agg_df = grouped.agg({primary_num: ["mean", "sum", "min", "max", "std"]})
    results["aggregated_cube"] = agg_df

    # 3. groupby.transform(): Group-level standardization / demean
    transform_series = grouped[primary_num].transform(lambda x: x - x.mean())
    df_with_demean = df.copy()
    df_with_demean[f"{primary_num}_demeaned"] = transform_series
    results["transformed_group"] = df_with_demean

    # 4. groupby.size(): Group frequency counts
    group_sizes = grouped.size()
    results["group_sizes"] = group_sizes.to_frame(name="group_count")

    # 5. Series.value_counts(): Categorical value frequency distribution
    cat_col = "trading_signal" if "trading_signal" in df.columns else group_col
    val_counts = df[cat_col].value_counts()
    results["value_counts"] = val_counts.to_frame(name="occurrence_count")

    # 6. df.nunique(): Unique entity cardinality analysis
    cardinality = df.nunique()
    results["nunique_cardinality"] = cardinality.to_frame(name="unique_entity_count")

    # 7. pd.crosstab(): Cross-tabulation contingency table
    if "trading_signal" in df.columns and "asset_category" in df.columns:
        cross_tab = pd.crosstab(df["asset_category"], df["trading_signal"], margins=True)
    else:
        dummy_cat = pd.cut(df[primary_num], bins=2, labels=["Low", "High"])
        cross_tab = pd.crosstab(df[group_col], dummy_cat)
    results["crosstab_matrix"] = cross_tab

    return results
