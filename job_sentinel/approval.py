"""
Human Approval Workflow Manager for JobSentinel.
Generates 10 AM Daily Digest (Top 5 jobs), formats approval requests for WhatsApp/Email,
parses user reply commands (e.g., 'YES 1,3'), and strictly enforces MANUAL submission.
"""

import logging
from typing import List, Dict, Any, Tuple
from job_sentinel.discovery import JobPosting

logger = logging.getLogger("JobSentinel.Approval")


class ApprovalManager:
    """Manages daily digest formatting and human approval workflow."""

    def __init__(self):
        self.pending_approvals: List[Dict[str, Any]] = []

    def generate_daily_digest(
        self,
        scored_packages: List[Dict[str, Any]],
        top_k: int = 5,
    ) -> str:
        """
        Formats 10 AM Daily Digest with Top 5 jobs:
        Company | Role | Score | Why I fit | Resume Link | Cover Letter
        """
        top_packages = scored_packages[:top_k]
        self.pending_approvals = top_packages

        if not top_packages:
            return "📬 JobSentinel Daily Digest (10 AM)\n\nNo job postings scored above the 75% suitability threshold today."

        digest_lines = [
            "📬 JobSentinel Daily Digest (10 AM)",
            "=========================================",
            f"Top {len(top_packages)} Matched Opportunities (Score >75%):\n",
        ]

        for idx, pkg in enumerate(top_packages, 1):
            company = pkg.get("company", "N/A")
            role = pkg.get("title", "N/A")
            score = pkg.get("score", 0.0)
            breakdown = pkg.get("breakdown", {})
            why_fit = breakdown.get("fit_reason", "High skill and domain match")
            folder = pkg.get("package_folder", "")
            resume_link = f"{folder}/resume.md"
            cover_letter_link = f"{folder}/cover_letter.md"

            digest_lines.append(
                f"[{idx}] {company} | {role} | Score: {score}%\n"
                f"    Why I fit: {why_fit}\n"
                f"    Resume Link: {resume_link}\n"
                f"    Cover Letter: {cover_letter_link}\n"
            )

        digest_lines.append(
            "=========================================\n"
            "Action Required: Reply with 'YES 1,3' to approve applications 1 and 3 for manual submission.\n"
            "CRITICAL: JobSentinel will prepare application packages, but NEVER submits automatically."
        )

        return "\n".join(digest_lines)

    def parse_approval_reply(self, reply_text: str) -> List[int]:
        """
        Parses approval reply, e.g. 'YES 1,3' -> [1, 3] or 'YES 1 2' -> [1, 2].
        """
        text = reply_text.strip().upper()
        if not text.startswith("YES"):
            logger.info("Reply does not indicate approval (must start with 'YES').")
            return []

        # Extract digits after 'YES'
        raw_ids = text.replace("YES", "").strip()
        import re

        indices = [int(n) for n in re.findall(r"\b\d+\b", raw_ids)]
        return indices

    def process_approvals(self, reply_text: str) -> List[Dict[str, Any]]:
        """
        Processes human reply, marking selected jobs READY_FOR_MANUAL_APPLY.
        Strictly guarantees NO automatic clicking or submission.
        """
        approved_indices = self.parse_approval_reply(reply_text)
        approved_packages: List[Dict[str, Any]] = []

        for idx in approved_indices:
            if 1 <= idx <= len(self.pending_approvals):
                pkg = self.pending_approvals[idx - 1]
                pkg["status"] = "READY_FOR_MANUAL_APPLY"
                approved_packages.append(pkg)
                logger.info(
                    f"Approved Job [{idx}]: {pkg.get('company')} - {pkg.get('title')} "
                    f"marked as READY_FOR_MANUAL_APPLY."
                )
            else:
                logger.warning(f"Invalid approval index: {idx}")

        return approved_packages
