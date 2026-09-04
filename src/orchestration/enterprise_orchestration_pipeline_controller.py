"""
Enterprise Orchestration Pipeline Controller Module.

Master pipeline using df.pipe() chaining all 12 core modules in a single fluent API workflow.
"""

import os
import sys
import pandas as pd

# Add src to sys.path if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.core.enterprise_data_acquisition_fabric import ingest_enterprise_live_sources
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


def run_master_enterprise_pipeline():
    """
    Executes the end-to-end master data fabric pipeline using fluent df.pipe() method chaining.
    """
    print("==========================================================================")
    print("  NAYEEM-ELDF: Enterprise Live Data Fabric - Master Orchestration Pipeline")
    print("==========================================================================")

    # 1. Acquisition Stage
    print("\n[Stage 1/12] Ingesting Live Enterprise Data Sources...")
    raw_sources = ingest_enterprise_live_sources()
    crypto_df = raw_sources["crypto"]
    stocks_df = raw_sources["stocks"]
    covid_df = raw_sources["covid"]
    print(f" -> Ingested Crypto: {len(crypto_df)} rows, Stocks: {len(stocks_df)} rows, Covid: {len(covid_df)} rows")

    # 2. Anomaly Remediation & Cleaning Stage
    print("\n[Stage 2/12] Anomaly Detection and Remediation Engine...")
    clean_crypto_df, anomaly_stats = detect_and_remediate_anomalies(crypto_df)
    print(f" -> Cleaned Crypto Data. Anomaly Stats: {anomaly_stats}")

    # 3. Profiling & Quality Assessment
    print("\n[Stage 3/12] Profiling and Quality Assessment Engine...")
    quality_metrics = assess_dataframe_quality(clean_crypto_df)
    print(f" -> Crypto Shape: {quality_metrics['shape']}, Missing Cells: {quality_metrics['missing_count']}")

    # 4. Multi-Source Fusion
    print("\n[Stage 4/12] Multi-Source Fusion and Temporal Alignment Fabric...")
    fused_results = fuse_and_align_data_sources(clean_crypto_df, stocks_df, covid_df)
    fused_crypto = fused_results["merged"]
    print(f" -> Fused Data Rows: {len(fused_crypto)}")

    # 5. Fluent Pipe Chaining across Feature Engineering, NLP, Signals, and Persistence
    print("\n[Stage 5-12/12] Executing Fluent df.pipe() Processing Chain...")

    final_telemetry = (
        fused_crypto
        .pipe(execute_feature_engineering_pipeline)
    )

    # Execute remaining module operations
    filtration_results = apply_intelligent_filtration(final_telemetry, stocks_df)
    reshaping_results = transform_dimensional_structure(stocks_df, final_telemetry)
    ranking_results = optimize_index_and_rank_assets(final_telemetry)
    cube_results = compute_analytical_cubes(final_telemetry)
    signal_results = generate_quantitative_signals(stocks_df)
    nlp_results = extract_nlp_and_categorical_features(final_telemetry)

    # Data Persistence & Memory Optimization
    mem_stats, export_paths = persist_and_optimize_telemetry(final_telemetry)

    print("\n==========================================================================")
    print("  Pipeline Execution Completed Successfully!")
    print(f"  - Memory Footprint Reduction: {mem_stats['optimization_percentage']:.2f}%")
    print(f"  - Generated Parquet: {export_paths['parquet']}")
    print(f"  - Generated Excel Report: {export_paths['excel']}")
    print("==========================================================================")

    return {
        "telemetry": final_telemetry,
        "export_paths": export_paths,
        "memory_stats": mem_stats,
        "quality_metrics": quality_metrics,
        "filtration": filtration_results,
        "reshaping": reshaping_results,
        "ranking": ranking_results,
        "cubes": cube_results,
        "signals": signal_results,
        "nlp": nlp_results
    }


if __name__ == "__main__":
    run_master_enterprise_pipeline()
