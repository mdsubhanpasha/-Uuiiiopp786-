"""Automated Container & Dependency Security Auditor Script.

Simulates vulnerability scanning for Python dependencies and audits
Dockerfile configuration against CloudNative security best practices.
"""

import argparse
import json
import logging
import os
import re
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("SecurityAudit")


class SecurityAuditor:
    """Production Security Compliance Auditor for Container & Dependencies."""

    def __init__(
        self,
        dockerfile_path: str = "Dockerfile",
        requirements_path: str = "requirements.txt",
    ) -> None:
        """Initialize SecurityAuditor with target file paths.

        Args:
            dockerfile_path: Path to Dockerfile.
            requirements_path: Path to requirements.txt.
        """
        self.dockerfile_path = dockerfile_path
        self.requirements_path = requirements_path

    def audit_dependencies(self) -> Dict[str, Any]:
        """Audit Python dependencies in requirements.txt.

        Returns:
            Dict containing dependency audit findings and vulnerability count.
        """
        findings: List[Dict[str, str]] = []
        if not os.path.exists(self.requirements_path):
            return {
                "status": "FAILED",
                "error": (
                    f"Requirements file '{self.requirements_path}' not found."
                ),
                "vulnerabilities_found": 1,
            }

        with open(self.requirements_path, "r", encoding="utf-8") as f:
            lines = [
                line.strip()
                for line in f
                if line.strip() and not line.startswith("#")
            ]

        # Known mock vulnerability database for simulation
        mock_vulnerabilities = {
            "fastapi": "<0.90.0",
            "requests": "<2.25.0",
            "urllib3": "<1.26.0",
            "pydantic": "<1.10.0",
        }

        pinned_count = 0
        unpinned_deps: List[str] = []

        for line in lines:
            if ">=" in line or "==" in line or "~=" in line:
                pinned_count += 1
            else:
                unpinned_deps.append(line)

            for pkg, vuln_version in mock_vulnerabilities.items():
                if line.startswith(pkg) and "==" in line:
                    ver = line.split("==")[1]
                    # Simple check simulation
                    if ver.startswith("0.8") or ver.startswith("1.24"):
                        findings.append({
                            "package": pkg,
                            "severity": "HIGH",
                            "cve": "CVE-2023-SIMULATED",
                            "description": (
                                f"Package {pkg} version {ver} is vulnerable."
                            ),
                        })

        if unpinned_deps:
            findings.append({
                "package": ", ".join(unpinned_deps),
                "severity": "LOW",
                "cve": "BEST_PRACTICE_WARNING",
                "description": (
                    "Dependencies should have explicit version constraints."
                ),
            })

        return {
            "total_dependencies": len(lines),
            "pinned_dependencies": pinned_count,
            "vulnerabilities": findings,
            "vulnerabilities_found": len([
                f for f in findings if f["severity"] in ("HIGH", "CRITICAL")
            ]),
        }

    def audit_dockerfile(self) -> Dict[str, Any]:
        """Audit Dockerfile configuration against container security rules.

        Returns:
            Dict containing check items, passed rules, and compliance score.
        """
        checks = {
            "multi_stage_build": {
                "passed": False,
                "description": "Uses multi-stage build strategy",
            },
            "non_root_user": {
                "passed": False,
                "description": "Runs as non-root user (USER directive)",
            },
            "slim_base_image": {
                "passed": False,
                "description": "Uses minimal/slim base image",
            },
            "healthcheck_defined": {
                "passed": False,
                "description": "Includes HEALTHCHECK directive",
            },
            "no_secrets_exposed": {
                "passed": True,
                "description": "No hardcoded credentials/secrets found",
            },
            "no_latest_tag": {
                "passed": True,
                "description": "Avoids using unpinned ':latest' base tag",
            },
        }

        if not os.path.exists(self.dockerfile_path):
            return {
                "status": "FAILED",
                "error": f"Dockerfile '{self.dockerfile_path}' not found.",
                "score_percent": 0.0,
            }

        with open(self.dockerfile_path, "r", encoding="utf-8") as f:
            content = f.read()

        from_count = len(re.findall(r"^FROM\s+", content, re.MULTILINE))
        if from_count >= 2:
            checks["multi_stage_build"]["passed"] = True

        if re.search(r"^USER\s+(?!root\b)\w+", content, re.MULTILINE):
            checks["non_root_user"]["passed"] = True

        if (
            re.search(r"FROM\s+python:[\d\.]+-slim", content, re.IGNORECASE)
            or "alpine" in content
        ):
            checks["slim_base_image"]["passed"] = True

        if "HEALTHCHECK" in content:
            checks["healthcheck_defined"]["passed"] = True

        # Secret pattern check
        secret_keywords = [
            "SECRET",
            "PASSWORD",
            "PRIVATE_KEY",
            "AWS_ACCESS_KEY",
        ]
        for kw in secret_keywords:
            if re.search(rf"ENV\s+.*{kw}\s*=", content, re.IGNORECASE):
                checks["no_secrets_exposed"]["passed"] = False
                checks["no_secrets_exposed"]["description"] = (
                    f"Potential secret exposure: {kw}"
                )

        if re.search(r"FROM\s+\w+:latest", content, re.IGNORECASE):
            checks["no_latest_tag"]["passed"] = False

        passed_count = sum(1 for c in checks.values() if c["passed"])
        score_percent = round((passed_count / len(checks)) * 100, 2)

        return {
            "checks": checks,
            "passed_rules": passed_count,
            "total_rules": len(checks),
            "score_percent": score_percent,
        }

    def run_full_audit(self) -> Dict[str, Any]:
        """Execute complete security audit for dependencies and Dockerfile.

        Returns:
            Dict with overall security status and report details.
        """
        logger.info("Executing CloudNative Container Security Audit...")
        dep_audit = self.audit_dependencies()
        docker_audit = self.audit_dockerfile()

        is_passed = (
            dep_audit.get("vulnerabilities_found", 0) == 0
            and docker_audit.get("score_percent", 0.0) >= 80.0
        )

        overall_score = docker_audit.get("score_percent", 0.0)

        report = {
            "audit_status": "PASSED" if is_passed else "FAILED",
            "overall_compliance_score": overall_score,
            "dependency_audit": dep_audit,
            "dockerfile_audit": docker_audit,
            "security_summary": (
                f"Container security score: {overall_score}%. "
                f"Vulnerabilities found: "
                f"{dep_audit.get('vulnerabilities_found', 0)}."
            ),
        }

        logger.info(
            "Audit Complete. Status: %s | Score: %s%%",
            report["audit_status"],
            report["overall_compliance_score"],
        )

        return report


def main() -> None:
    """CLI entrypoint for Security Auditor."""
    parser = argparse.ArgumentParser(
        description="Automated Container & Dependency Security Auditor"
    )
    parser.add_argument(
        "--dockerfile",
        type=str,
        default="Dockerfile",
        help="Path to Dockerfile.",
    )
    parser.add_argument(
        "--requirements",
        type=str,
        default="requirements.txt",
        help="Path to requirements.txt.",
    )
    parser.add_argument(
        "--json-out",
        type=str,
        default="",
        help="Optional path to write JSON report.",
    )

    args = parser.parse_args()
    auditor = SecurityAuditor(
        dockerfile_path=args.dockerfile,
        requirements_path=args.requirements,
    )
    report = auditor.run_full_audit()

    report_json = json.dumps(report, indent=2)
    print("\n" + "=" * 60)
    print("SECURITY AUDIT REPORT")
    print("=" * 60)
    print(report_json)

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            f.write(report_json)
        logger.info("Audit report saved to: %s", args.json_out)

    if report["audit_status"] != "PASSED":
        exit(1)


if __name__ == "__main__":
    main()
