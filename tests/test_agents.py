"""Unit tests for FinAgent-Ops multi-agent modules."""

import os
import pytest

from src.agents.ingest_agent import IngestionAgent
from src.agents.recon_agent import ReconciliationAgent
from src.agents.audit_agent import ForensicAuditAgent
from src.agents.report_agent import ReportAgent


@pytest.fixture
def ledger_csv():
    """Fixture returning ledger CSV path."""
    return "data/sample_ledger.csv"


@pytest.fixture
def bank_csv():
    """Fixture returning bank statement CSV path."""
    return "data/bank_statement.csv"


def test_ingestion_agent(ledger_csv, bank_csv):
    """Test IngestionAgent CSV parsing and schema validation."""
    agent = IngestionAgent()
    res = agent.process(ledger_csv, bank_csv)

    assert "normalized_ledger" in res
    assert "normalized_bank" in res
    assert len(res["normalized_ledger"]) > 0
    assert len(res["normalized_bank"]) > 0
    assert isinstance(res["ingestion_errors"], list)


def test_reconciliation_agent(ledger_csv, bank_csv):
    """Test ReconciliationAgent rule matching and ML anomaly detection."""
    ingest = IngestionAgent()
    ingest_res = ingest.process(ledger_csv, bank_csv)

    l_records = ingest_res["normalized_ledger"]
    b_records = ingest_res["normalized_bank"]

    recon = ReconciliationAgent(contamination=0.15)
    matched, discrepancies = recon.reconcile(l_records, b_records)

    assert len(matched) > 0
    assert len(discrepancies) > 0
    assert any(
        d["discrepancy_type"] == "AMOUNT_MISMATCH" for d in discrepancies
    )


def test_forensic_audit_agent(ledger_csv, bank_csv):
    """Test ForensicAuditAgent tool calling and CoT reasoning trace."""
    ingest = IngestionAgent()
    ingest_res = ingest.process(ledger_csv, bank_csv)
    l_records = ingest_res["normalized_ledger"]
    b_records = ingest_res["normalized_bank"]

    recon = ReconciliationAgent()
    matched, discrepancies = recon.reconcile(l_records, b_records)

    auditor = ForensicAuditAgent()
    audit_results = auditor.process(discrepancies, l_records, b_records)

    assert len(audit_results) == len(discrepancies)
    assert "risk_level" in audit_results[0]
    assert "cot_reasoning_trace" in audit_results[0]
    assert len(audit_results[0]["cot_reasoning_trace"]) > 0


def test_report_agent(ledger_csv, bank_csv, tmp_path):
    """Test ReportAgent PDF and JSON artifact generation."""
    ingest = IngestionAgent()
    ingest_res = ingest.process(ledger_csv, bank_csv)
    l_records = ingest_res["normalized_ledger"]
    b_records = ingest_res["normalized_bank"]

    recon = ReconciliationAgent()
    matched, discrepancies = recon.reconcile(l_records, b_records)

    auditor = ForensicAuditAgent()
    audit_results = auditor.process(discrepancies, l_records, b_records)

    output_dir = str(tmp_path / "artifacts")
    reporter = ReportAgent(output_dir=output_dir)
    res = reporter.process(
        l_records, b_records, matched, discrepancies, audit_results
    )

    assert os.path.exists(res["json_report_path"])
    assert os.path.exists(res["pdf_report_path"])
    assert res["summary"]["discrepancy_count"] == len(discrepancies)
