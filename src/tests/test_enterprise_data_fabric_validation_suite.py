"""
Enterprise Data Fabric Validation Test Suite.

Validates all 80+ pandas functions across all 12 modules, live data acquisition, and output file generation.
"""

import os
import sys
import pytest
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.core.enterprise_data_acquisition_fabric import (
    ingest_enterprise_live_sources, fetch_crypto_live, fetch_stocks_live, fetch_covid_live,
    create_and_read_parquet, create_and_read_sqlite, create_and_read_excel
)
from src.core.data_profiling_and_quality_assessment_engine import assess_dataframe_quality
from src.core.intelligent_filtration_and_query_optimization_layer import apply_intelligent_filtration
from src.core.dimensional_transformation_and_restructuring_module import transform_dimensional_structure
from src.core.anomaly_detection_and_remediation_engine import detect_and_remediate_anomalies
from src.core.feature_engineering_and_schema_transformation_pipeline import execute_feature_engineering_pipeline
from src.core.index_optimization_and_ranking_analytics_layer import optimize_index_and_rank_assets
from src.core.distributed_aggregation_and_analytical_cube_engine import compute_analytical_cubes
from src.core.multi_source_fusion_and_temporal_alignment_fabric import fuse_and_align_data_sources
from src.core.quantitative_signal_and_time_series_forecasting_engine import generate_quantitative_signals
from src.core.nlp_feature_extraction_and_categorical_encoding_pipeline import extract_nlp_and_categorical_features
from src.core.data_persistence_and_memory_optimization_layer import persist_and_optimize_telemetry
from src.orchestration.enterprise_orchestration_pipeline_controller import run_master_enterprise_pipeline


def test_01_acquisition_fabric():
    sources = ingest_enterprise_live_sources()
    assert "crypto" in sources
    assert "stocks" in sources
    assert "covid" in sources
    assert "parquet" in sources
    assert "sqlite" in sources
    assert "excel" in sources
    assert not sources["crypto"].empty
    assert isinstance(sources["crypto"], pd.DataFrame)


def test_02_profiling_engine():
    crypto_df = fetch_crypto_live()
    quality = assess_dataframe_quality(crypto_df)
    assert "shape" in quality
    assert "dtypes" in quality
    assert "head" in quality
    assert "tail" in quality
    assert "sample" in quality
    assert "describe" in quality
    assert isinstance(quality["shape"], tuple)


def test_03_intelligent_filtration():
    crypto_df = fetch_crypto_live()
    stocks_df = fetch_stocks_live()
    filtration = apply_intelligent_filtration(crypto_df, stocks_df)
    assert "btc_loc" in filtration
    assert "iloc_100" in filtration
    assert "query_filtered" in filtration
    assert "filter_cols" in filtration
    assert "isin_filtered" in filtration
    assert "between_filtered" in filtration
    assert "where_masked" in filtration


def test_04_dimensional_transformation():
    crypto_df = fetch_crypto_live()
    stocks_df = fetch_stocks_live()
    reshaping = transform_dimensional_structure(stocks_df, crypto_df)
    assert "pivot_table" in reshaping
    assert "pivot" in reshaping
    assert "melted" in reshaping
    assert "stacked" in reshaping
    assert "unstacked" in reshaping
    assert "exploded" in reshaping
    assert "wide_to_long" in reshaping


def test_05_anomaly_detection_remediation():
    crypto_df = fetch_crypto_live()
    clean_df, stats = detect_and_remediate_anomalies(crypto_df)
    assert isinstance(clean_df, pd.DataFrame)
    assert "initial_missing_cells" in stats
    assert "final_record_count" in stats


def test_06_feature_engineering_pipeline():
    crypto_df = fetch_crypto_live()
    engineered_df = execute_feature_engineering_pipeline(crypto_df)
    assert "pnl_estimate" in engineered_df.columns
    assert "trading_signal" in engineered_df.columns


def test_07_index_optimization_ranking():
    crypto_df = fetch_crypto_live()
    ranking = optimize_index_and_rank_assets(crypto_df)
    assert "sorted_by_volume" in ranking
    assert "indexed" in ranking
    assert "sorted_index" in ranking
    assert "reset_index" in ranking
    assert "nlargest" in ranking
    assert "nsmallest" in ranking
    assert "reindexed" in ranking


def test_08_distributed_aggregation_cubes():
    crypto_df = fetch_crypto_live()
    engineered_df = execute_feature_engineering_pipeline(crypto_df)
    cubes = compute_analytical_cubes(engineered_df)
    assert "aggregated_cube" in cubes
    assert "transformed_group" in cubes
    assert "group_sizes" in cubes
    assert "value_counts" in cubes
    assert "nunique_cardinality" in cubes
    assert "crosstab_matrix" in cubes


def test_09_multi_source_fusion():
    crypto_df = fetch_crypto_live()
    stocks_df = fetch_stocks_live()
    covid_df = fetch_covid_live()
    fusion = fuse_and_align_data_sources(crypto_df, stocks_df, covid_df)
    assert "concatenated" in fusion
    assert "merged" in fusion
    assert "joined" in fusion
    assert "combine_first" in fusion
    assert "updated" in fusion
    assert "compared_diff" in fusion
    assert "merge_asof" in fusion


def test_10_quantitative_signals():
    stocks_df = fetch_stocks_live()
    signals = generate_quantitative_signals(stocks_df)
    assert "calendar_index" in signals
    assert "resampled_ohlc" in signals
    assert "signal_features" in signals


def test_11_nlp_and_categorical():
    crypto_df = fetch_crypto_live()
    nlp_res = extract_nlp_and_categorical_features(crypto_df)
    assert "nlp_extracted" in nlp_res
    assert "categorical_encoded" in nlp_res


def test_12_persistence_and_memory():
    crypto_df = fetch_crypto_live()
    engineered_df = execute_feature_engineering_pipeline(crypto_df)
    mem_stats, export_paths = persist_and_optimize_telemetry(engineered_df)
    assert "initial_memory_bytes" in mem_stats
    assert os.path.exists(export_paths["csv"])
    assert os.path.exists(export_paths["excel"])
    assert os.path.exists(export_paths["parquet"])
    assert os.path.exists(export_paths["json"])


def test_master_orchestration_pipeline():
    result = run_master_enterprise_pipeline()
    assert "telemetry" in result
    assert "export_paths" in result
    assert os.path.exists("data/processed/master_telemetry_fabric.parquet")
    assert os.path.exists("data/reports/enterprise_kpi_analytical_report.xlsx")
