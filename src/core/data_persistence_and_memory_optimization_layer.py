"""
Data Persistence and Memory Optimization Layer Module.

Required Functions:
- df.to_csv()
- df.to_excel()
- df.to_parquet()
- df.eval()
- df.to_json()
- df.memory_usage()
- df.convert_dtypes()

Logic: to_csv, to_excel 2 sheets, to_parquet, eval signal, to_json API, memory_usage before/after, convert_dtypes 60% optimization.
"""

import os
from typing import Dict, Tuple, Any
import pandas as pd


def persist_and_optimize_telemetry(df: pd.DataFrame) -> Tuple[Dict[str, Any], Dict[str, str]]:
    """
    Applies vector expression evaluation, memory optimization via convert_dtypes, and multi-format persistence.
    """
    optimized_df = df.copy()

    # 1. df.eval(): Fast C-speed vector expression evaluation for trading signals or profit calculation
    if "unit_price" in optimized_df.columns and "trade_volume" in optimized_df.columns:
        optimized_df = optimized_df.eval("market_val = unit_price * trade_volume")
    elif "close" in optimized_df.columns and "volume" in optimized_df.columns:
        optimized_df = optimized_df.eval("market_val = close * volume")
    else:
        optimized_df["market_val"] = 1000.0

    # 2. df.memory_usage(): Calculate initial memory footprint
    initial_mem_bytes = optimized_df.memory_usage(deep=True).sum()

    # 3. df.convert_dtypes(): Cast python objects to high-efficiency Arrow/Pandas extension dtypes
    converted_df = optimized_df.convert_dtypes()
    optimized_mem_bytes = converted_df.memory_usage(deep=True).sum()

    memory_stats = {
        "initial_memory_bytes": int(initial_mem_bytes),
        "optimized_memory_bytes": int(optimized_mem_bytes),
        "optimization_percentage": float(max(0.0, (1.0 - (optimized_mem_bytes / max(1, initial_mem_bytes))) * 100))
    }

    # Ensure target output directories exist
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("data/reports", exist_ok=True)

    file_paths = {}

    # 4. df.to_csv(): Standard CSV export
    csv_path = "data/processed/master_telemetry.csv"
    converted_df.to_csv(csv_path, index=False)
    file_paths["csv"] = csv_path

    # 5. df.to_excel(): Export 2 sheets to Excel report file
    excel_path = "data/reports/enterprise_kpi_analytical_report.xlsx"
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        converted_df.to_excel(writer, sheet_name="Master_Telemetry", index=False)
        memory_summary = pd.DataFrame([memory_stats])
        memory_summary.to_excel(writer, sheet_name="Memory_Performance_KPI", index=False)
    file_paths["excel"] = excel_path

    # 6. df.to_parquet(): High performance Apache Parquet export
    parquet_path = "data/processed/master_telemetry_fabric.parquet"
    converted_df.to_parquet(parquet_path, index=False)
    file_paths["parquet"] = parquet_path

    # 7. df.to_json(): Compact API JSON export string / file
    json_path = "data/processed/master_telemetry.json"
    converted_df.to_json(json_path, orient="records", date_format="iso")
    file_paths["json"] = json_path

    return memory_stats, file_paths
