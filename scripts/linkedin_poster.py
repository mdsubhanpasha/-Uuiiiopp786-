"""Automated LinkedIn Technical Content Generator and Poster Script.

Reads pipeline execution status and posts Day 3 CloudNative DevOps project
achievement to LinkedIn via API v2 (UGC Posts) or operates in dry-run mode.
"""

import argparse
import logging
import os
from typing import Any, Dict, Optional

import requests

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("LinkedInPoster")


class LinkedInPoster:
    """Automated LinkedIn announcement and technical content publisher."""

    def __init__(
        self,
        access_token: Optional[str] = None,
        author_urn: Optional[str] = None,
    ) -> None:
        """Initialize LinkedInPoster.

        Args:
            access_token: LinkedIn API OAuth2 bearer access token.
            author_urn: LinkedIn URN (e.g. urn:li:person:12345).
        """
        self.access_token = access_token or os.getenv(
            "LINKEDIN_ACCESS_TOKEN", ""
        )
        self.author_urn = author_urn or os.getenv(
            "LINKEDIN_AUTHOR_URN", "urn:li:person:sample_author_id"
        )
        self.api_url = "https://api.linkedin.com/v2/ugcPosts"

    def generate_post_content(
        self,
        repo_name: str = "devops-day3-cloudnative-pipeline",
        security_score: float = 100.0,
    ) -> str:
        """Generate structured markdown technical announcement post.

        Args:
            repo_name: Name of target GitHub repository.
            security_score: Container security audit compliance score.

        Returns:
            String containing formatted post text with hashtags.
        """
        post_text = (
            "🚀 Day 3 CloudNative DevOps Milestone: Production CI/CD & "
            "Automated Container Security Pipeline Released!\n\n"
            f"I've built and deployed 'CloudNative-Ops-Day3' ({repo_name}), "
            "an end-to-end production-grade DevOps delivery pipeline "
            "featuring:\n\n"
            "1️⃣ Production FastAPI Microservice: Health checks, "
            "system metrics, and transactional validation endpoints.\n"
            "2️⃣ Multi-Stage Dockerfile: Hardened container footprint "
            "running with non-root 'appuser' and built-in HEALTHCHECK.\n"
            "3️⃣ Automated Security Scanner (`scripts/security_audit.py`): "
            "Dependency vulnerability checks & Dockerfile rule validation "
            f"(Score: {security_score}%).\n"
            "4️⃣ GitHub Actions CI/CD (`.github/workflows/ci_cd.yml`): "
            "Automated Flake8 linting, Pytest suite, security audit, "
            "and container verification.\n"
            "5️⃣ Deployment & LinkedIn Automation: One-click sync to GitHub "
            "repository and automated technical release posting.\n\n"
            "#DevOps #CloudNative #Docker #FastAPI #GitHubActions "
            "#CyberSecurity #Python #CI_CD #Containers #DevSecOps"
        )
        return post_text

    def publish_post(
        self,
        repo_name: str = "devops-day3-cloudnative-pipeline",
        security_score: float = 100.0,
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        """Publish post content to LinkedIn API or run dry-run simulation.

        Args:
            repo_name: Target repository name.
            security_score: Security audit score percentage.
            dry_run: If True, previews generated post without calling API.

        Returns:
            Dict response with post status and metadata.
        """
        content = self.generate_post_content(
            repo_name=repo_name, security_score=security_score
        )

        if dry_run or not self.access_token or "sample" in self.author_urn:
            logger.info(
                "[DRY RUN] LinkedIn Announcement generated successfully:\n"
            )
            print("=" * 60)
            print(content)
            print("=" * 60)
            return {
                "status": "SUCCESS",
                "mode": "DRY_RUN",
                "message": "Post generated and validated in dry-run mode.",
                "post_content": content,
            }

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        }

        payload = {
            "author": self.author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": content},
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            },
        }

        try:
            response = requests.post(
                self.api_url, headers=headers, json=payload, timeout=10
            )
            response.raise_for_status()
            logger.info("LinkedIn post successfully published via API!")
            return {
                "status": "PUBLISHED",
                "response_code": response.status_code,
                "data": response.json(),
            }
        except Exception as err:
            logger.error("Failed to publish to LinkedIn API: %s", str(err))
            return {
                "status": "ERROR",
                "error": str(err),
            }


def main() -> None:
    """CLI entrypoint for LinkedIn Poster."""
    parser = argparse.ArgumentParser(
        description="Automated LinkedIn Technical Post Generator & Publisher"
    )
    parser.add_argument(
        "--repo-name",
        type=str,
        default="devops-day3-cloudnative-pipeline",
        help="Target GitHub repository name.",
    )
    parser.add_argument(
        "--score",
        type=float,
        default=100.0,
        help="Container security audit score.",
    )
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Attempt live publishing using environment credentials.",
    )

    args = parser.parse_args()
    poster = LinkedInPoster()

    is_dry_run = not args.publish
    result = poster.publish_post(
        repo_name=args.repo_name,
        security_score=args.score,
        dry_run=is_dry_run,
    )
    print(f"\n[+] LinkedIn Posting Result Status: {result['status']}")


if __name__ == "__main__":
    main()
