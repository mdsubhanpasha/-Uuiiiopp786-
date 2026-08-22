"""FinAgent-Ops: Autonomous Multi-Agent Financial Reconciliation Engine.

Provides FastAPI Web Service API endpoints and CLI mode execution.
"""

import argparse
import json
import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import uvicorn

from scripts.github_deploy import GitHubDeployer
from scripts.linkedin_poster import LinkedInPoster
from src.graph_orchestrator import FinAgentOrchestrator
from src.models import (
    DeployRequest,
    DeployResponse,
    ReconcileRequest,
    ReconcileResponse,
)

app = FastAPI(
    title="FinAgent-Ops API",
    description=(
        "Autonomous Multi-Agent Financial Reconciliation & Fraud "
        "Detection Engine"
    ),
    version="1.0.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check REST endpoint."""
    return {"status": "healthy", "service": "FinAgent-Ops"}


@app.post("/api/v1/reconcile", response_model=ReconcileResponse)
def api_reconcile(req: ReconcileRequest) -> ReconcileResponse:
    """Trigger multi-agent financial reconciliation and audit workflow."""
    l_path = req.ledger_csv_path or "data/sample_ledger.csv"
    b_path = req.bank_csv_path or "data/bank_statement.csv"

    if not os.path.exists(l_path):
        raise HTTPException(
            status_code=404, detail=f"Ledger file not found at {l_path}"
        )
    if not os.path.exists(b_path):
        raise HTTPException(
            status_code=404,
            detail=f"Bank statement file not found at {b_path}",
        )

    orchestrator = FinAgentOrchestrator()
    final_state = orchestrator.run(l_path, b_path)

    return ReconcileResponse(
        status="success",
        summary=final_state.get("report_summary", {}),
        discrepancy_count=len(final_state.get("discrepancies", [])),
        audit_results=final_state.get("audit_results", []),
        pdf_report_path=final_state.get("pdf_report_path"),
    )


@app.get("/api/v1/reports/pdf")
def get_pdf_report(
    path: str = "artifacts/reconciliation_report.pdf",
) -> FileResponse:
    """Download generated PDF audit report."""
    if not os.path.exists(path):
        raise HTTPException(
            status_code=404, detail=f"PDF Report not found at {path}"
        )
    return FileResponse(
        path,
        media_type="application/pdf",
        filename="reconciliation_report.pdf",
    )


@app.post("/api/v1/deploy/github", response_model=DeployResponse)
def deploy_github(req: DeployRequest) -> DeployResponse:
    """Automate GitHub code commit and push."""
    deployer = GitHubDeployer()
    res = deployer.deploy(
        commit_message=req.commit_message or "Deploy FinAgent-Ops release",
        dry_run=req.dry_run,
    )
    return DeployResponse(status=res["status"], details=res)


@app.post("/api/v1/deploy/linkedin", response_model=DeployResponse)
def deploy_linkedin(req: DeployRequest) -> DeployResponse:
    """Automate technical post announcement publishing on LinkedIn."""
    poster = LinkedInPoster()
    res = poster.publish_post(dry_run=req.dry_run)
    return DeployResponse(status=res["status"], details=res)


def print_banner() -> None:
    """Print ASCII System Banner."""
    banner = (
        "=" * 80 + "\n"
        "   FINAGENT-OPS: AUTONOMOUS MULTI-AGENT FINANCIAL RECONCILIATION\n"
        + "=" * 80 + "\n"
        "Agents: Ingestion -> Recon (ML) -> Forensic Audit (CoT) -> Report\n"
        + "-" * 80 + "\n"
    )
    print(banner)


def run_cli_mode(ledger_path: str, bank_path: str) -> None:
    """Run CLI workflow execution."""
    print_banner()
    print(f"[+] Processing Ledger: {ledger_path}")
    print(f"[+] Processing Bank Statement: {bank_path}\n")

    orchestrator = FinAgentOrchestrator()
    final_state = orchestrator.run(ledger_path, bank_path)

    print("\n" + "=" * 80)
    print("WORKFLOW STATE TRANSITION LOGS:")
    for msg in final_state.get("messages", []):
        print(f"  {msg}")

    print("\n" + "=" * 80)
    print("EXECUTIVE SUMMARY:")
    print(json.dumps(final_state.get("report_summary", {}), indent=2))

    print("\n" + "=" * 80)
    print("FORENSIC AUDIT DISCREPANCY LOGS:")
    print(json.dumps(final_state.get("audit_results", []), indent=2))
    print("=" * 80 + "\n")


def main() -> None:
    """Main application entry point."""
    parser = argparse.ArgumentParser(
        description="FinAgent-Ops Enterprise Application Runner"
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="cli",
        choices=["cli", "api"],
        help="Execution mode: 'cli' or 'api' server.",
    )
    parser.add_argument(
        "--ledger",
        type=str,
        default="data/sample_ledger.csv",
        help="Path to ledger CSV file.",
    )
    parser.add_argument(
        "--bank",
        type=str,
        default="data/bank_statement.csv",
        help="Path to bank statement CSV file.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port number for FastAPI server mode.",
    )

    args = parser.parse_args()

    if args.mode == "api":
        print_banner()
        print(f"[+] Starting FastAPI server on port {args.port}...")
        uvicorn.run(app, host="0.0.0.0", port=args.port)
    else:
        run_cli_mode(args.ledger, args.bank)


if __name__ == "__main__":
    main()
