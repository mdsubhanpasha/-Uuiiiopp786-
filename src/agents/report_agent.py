"""Report and Artifact Generation Agent for FinAgent-Ops."""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List

from fpdf import FPDF

from src.models import AuditReportSummary

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ReportAgent")


class PDFReportGenerator(FPDF):
    """Custom FPDF class for generating formatted audit reports."""

    def header(self) -> None:
        """Page header layout."""
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(24, 43, 73)
        self.cell(
            0,
            10,
            "FinAgent-Ops: Financial Reconciliation & Forensic Audit",
            border=False,
            new_x="LMARGIN",
            new_y="NEXT",
            align="C",
        )
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(100, 100, 100)
        date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cell(
            0,
            5,
            f"Generated on: {date_str} UTC",
            border=False,
            new_x="LMARGIN",
            new_y="NEXT",
            align="C",
        )
        self.ln(5)

    def footer(self) -> None:
        """Page footer layout."""
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(
            0, 10, f"Page {self.page_no()}", align="C"
        )


class ReportAgent:
    """Agent responsible for generating JSON artifacts and PDF reports."""

    def __init__(self, output_dir: str = "artifacts") -> None:
        """Initialize ReportAgent.

        Args:
            output_dir: Target directory for generated report artifacts.
        """
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def summarize_audit(
        self,
        ledger_records: List[Dict[str, Any]],
        bank_records: List[Dict[str, Any]],
        matched_records: List[Dict[str, Any]],
        discrepancies: List[Dict[str, Any]],
        audit_results: List[Dict[str, Any]],
    ) -> AuditReportSummary:
        """Calculate summary statistics for reconciliation run.

        Args:
            ledger_records: List of ledger transaction dicts.
            bank_records: List of bank transaction dicts.
            matched_records: List of matched transaction dicts.
            discrepancies: List of discrepancy dicts.
            audit_results: List of forensic audit result dicts.

        Returns:
            AuditReportSummary instance with aggregate metrics.
        """
        anomaly_count = sum(1 for d in discrepancies if d.get("is_anomaly"))
        high_risk_count = sum(
            1
            for a in audit_results
            if a.get("risk_level") in ["High", "Critical"]
        )

        l_amt = sum(float(r.get("amount", 0.0)) for r in ledger_records)
        b_amt = sum(float(r.get("amount", 0.0)) for r in bank_records)

        return AuditReportSummary(
            total_ledger_records=len(ledger_records),
            total_bank_records=len(bank_records),
            matched_count=len(matched_records),
            discrepancy_count=len(discrepancies),
            anomaly_count=anomaly_count,
            high_risk_count=high_risk_count,
            total_ledger_amount=round(l_amt, 2),
            total_bank_amount=round(b_amt, 2),
        )

    def generate_json_artifact(
        self,
        summary: AuditReportSummary,
        discrepancies: List[Dict[str, Any]],
        audit_results: List[Dict[str, Any]],
        filename: str = "reconciliation_summary.json",
    ) -> str:
        """Export audit artifacts into structured JSON format.

        Args:
            summary: AuditReportSummary metadata.
            discrepancies: List of discrepancy dicts.
            audit_results: List of forensic audit dicts.
            filename: Target file name.

        Returns:
            Filepath string to created JSON artifact.
        """
        filepath = os.path.join(self.output_dir, filename)
        artifact_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": summary.model_dump(),
            "discrepancies": discrepancies,
            "forensic_audit_results": audit_results,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(artifact_data, f, indent=2)

        logger.info("JSON Artifact generated at %s", filepath)
        return filepath

    def generate_pdf_report(
        self,
        summary: AuditReportSummary,
        discrepancies: List[Dict[str, Any]],
        audit_results: List[Dict[str, Any]],
        filename: str = "reconciliation_report.pdf",
    ) -> str:
        """Generate PDF report via FPDF engine.

        Args:
            summary: Summary metadata.
            discrepancies: List of discrepancy items.
            audit_results: List of forensic audit entries.
            filename: Target PDF filename.

        Returns:
            Filepath string to generated PDF report.
        """
        filepath = os.path.join(self.output_dir, filename)

        pdf = PDFReportGenerator()
        pdf.add_page()

        # Section 1: Executive Summary Metrics
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(24, 43, 73)
        pdf.cell(0, 8, "1. Executive Summary", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(0, 0, 0)

        summary_text = (
            f"Total Ledger Records: {summary.total_ledger_records}  "
            f"(Total Value: ${summary.total_ledger_amount:,.2f})\n"
            f"Total Bank Records: {summary.total_bank_records}  "
            f"(Total Value: ${summary.total_bank_amount:,.2f})\n"
            f"Matched Records: {summary.matched_count} | "
            f"Discrepancies: {summary.discrepancy_count}\n"
            f"ML Anomalies Flagged: {summary.anomaly_count} | "
            f"High/Critical Risk Items: {summary.high_risk_count}"
        )
        pdf.multi_cell(0, 6, summary_text)
        pdf.ln(4)

        # Section 2: Discrepancies & Anomaly Log
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(24, 43, 73)
        pdf.cell(
            0,
            8,
            "2. Discrepancy & ML Anomaly Breakdown",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        pdf.set_font("Helvetica", "", 9)

        audit_map = {a["discrepancy_id"]: a for a in audit_results}

        for disc in discrepancies:
            disc_id = disc["discrepancy_id"]
            d_type = disc["discrepancy_type"]
            amt_diff = disc["amount_difference"]
            is_anom = disc["is_anomaly"]
            audit_entry = audit_map.get(disc_id, {})
            risk = audit_entry.get("risk_level", "Unknown")

            if risk in ["Critical", "High"]:
                pdf.set_text_color(180, 0, 0)
            elif risk == "Medium":
                pdf.set_text_color(180, 100, 0)
            else:
                pdf.set_text_color(0, 100, 0)

            title = (
                f"[{disc_id}] {d_type} (Risk: {risk}) - Diff: ${amt_diff:,.2f}"
            )
            if is_anom:
                title += " [ML ANOMALY]"
            pdf.cell(0, 6, title, new_x="LMARGIN", new_y="NEXT")

            pdf.set_text_color(60, 60, 60)
            cause = audit_entry.get('root_cause_explanation', 'N/A')
            act = audit_entry.get('recommended_action', 'N/A')
            details = (
                f"Details: {disc.get('details')}\n"
                f"Root Cause: {cause}\n"
                f"Action: {act}"
            )
            pdf.multi_cell(0, 5, details)
            pdf.ln(2)

        pdf.output(filepath)
        logger.info("PDF Report generated at %s", filepath)
        return filepath

    def process(
        self,
        ledger_records: List[Dict[str, Any]],
        bank_records: List[Dict[str, Any]],
        matched_records: List[Dict[str, Any]],
        discrepancies: List[Dict[str, Any]],
        audit_results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Generate all summary artifacts and reports.

        Args:
            ledger_records: Ledger list.
            bank_records: Bank list.
            matched_records: Matched list.
            discrepancies: Discrepancy list.
            audit_results: Forensic audit list.

        Returns:
            Dict containing report summary and file paths.
        """
        summary = self.summarize_audit(
            ledger_records,
            bank_records,
            matched_records,
            discrepancies,
            audit_results,
        )
        json_path = self.generate_json_artifact(
            summary, discrepancies, audit_results
        )
        pdf_path = self.generate_pdf_report(
            summary, discrepancies, audit_results
        )

        return {
            "summary": summary.model_dump(),
            "json_report_path": json_path,
            "pdf_report_path": pdf_path,
        }
