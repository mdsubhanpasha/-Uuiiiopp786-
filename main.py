"""CloudNative DevOps Day 3 CLI and Orchestrator Entry Point.

Provides a unified command-line interface to start the FastAPI microservice,
run container security audits, deploy to GitHub, and announce releases.
"""

import argparse
import json
import sys

import uvicorn

from scripts.github_deploy import GitHubDeployer
from scripts.linkedin_poster import LinkedInPoster
from scripts.security_audit import SecurityAuditor


def print_banner() -> None:
    """Print ASCII banner for CloudNative-Ops-Day3 CLI."""
    banner = (
        "=" * 80 + "\n"
        "   CLOUD NATIVE OPS - DAY 3: PRODUCTION CI/CD & SECURITY PIPELINE\n"
        "          Target Repository: devops-day3-cloudnative-pipeline\n"
        + "=" * 80 + "\n"
        "Modes: --mode serve | audit | deploy | announce | demo\n"
        + "-" * 80 + "\n"
    )
    print(banner)


def run_demo() -> None:
    """Execute complete pipeline dry-run demonstration."""
    print_banner()
    print("[1] STAGE 1: EXECUTING CONTAINER & DEPENDENCY SECURITY AUDIT...")
    auditor = SecurityAuditor()
    audit_report = auditor.run_full_audit()
    print(
        f"-> Security Audit Result: {audit_report['audit_status']} "
        f"({audit_report['overall_compliance_score']}%)\n"
    )

    print("[2] STAGE 2: SIMULATING GITHUB REPOSITORY DEPLOYMENT...")
    deployer = GitHubDeployer(repo_name="devops-day3-cloudnative-pipeline")
    deploy_result = deployer.sync_and_deploy(dry_run=True)
    print(
        f"-> GitHub Deploy Result: {deploy_result['status']} "
        f"(Target: {deploy_result['target_repository']})\n"
    )

    print("[3] STAGE 3: GENERATING LINKEDIN ANNOUNCEMENT POST...")
    poster = LinkedInPoster()
    post_result = poster.publish_post(
        repo_name="devops-day3-cloudnative-pipeline",
        security_score=audit_report["overall_compliance_score"],
        dry_run=True,
    )
    print(f"-> LinkedIn Poster Status: {post_result['status']}\n")

    print("=" * 80)
    print("[+] DEMO PIPELINE COMPLETED SUCCESSFULLY!")
    print("=" * 80)


def main() -> None:
    """Main entrypoint for CloudNative-Ops-Day3 CLI."""
    parser = argparse.ArgumentParser(
        description=(
            "CloudNative-Ops-Day3: Production CI/CD & "
            "Container Security Pipeline CLI"
        )
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="demo",
        choices=["serve", "audit", "deploy", "announce", "demo"],
        help="Pipeline operation mode (default: demo).",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host address for FastAPI server.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for FastAPI server.",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help=(
            "Perform live deployment / posting "
            "instead of dry-run simulation."
        ),
    )

    args = parser.parse_args()

    if args.mode == "demo":
        run_demo()

    elif args.mode == "serve":
        print_banner()
        print(
            f"[+] Starting FastAPI microservice on "
            f"http://{args.host}:{args.port}"
        )
        uvicorn.run(
            "src.app:app", host=args.host, port=args.port, reload=False
        )

    elif args.mode == "audit":
        auditor = SecurityAuditor()
        report = auditor.run_full_audit()
        print(json.dumps(report, indent=2))
        if report["audit_status"] != "PASSED":
            sys.exit(1)

    elif args.mode == "deploy":
        deployer = GitHubDeployer()
        res = deployer.sync_and_deploy(dry_run=not args.live)
        print(json.dumps(res, indent=2))

    elif args.mode == "announce":
        poster = LinkedInPoster()
        res = poster.publish_post(dry_run=not args.live)
        print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
