"""Automated GitHub Deployment and Repository Synchronization Script.

Handles automated repository sync, staging, committing, and pushing
for the target repository: devops-day3-cloudnative-pipeline.
"""

import argparse
import logging
import os
import subprocess
from typing import Any, Dict, Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("GitHubDeploy")


class GitHubDeployer:
    """Automated deployment manager for devops-day3-cloudnative-pipeline."""

    def __init__(
        self,
        repo_name: str = "devops-day3-cloudnative-pipeline",
        token: Optional[str] = None,
    ) -> None:
        """Initialize GitHubDeployer.

        Args:
            repo_name: Target GitHub repository name.
            token: Personal Access Token for GitHub authentication.
        """
        self.repo_name = os.getenv("GITHUB_REPO_NAME", repo_name)
        self.token = token or os.getenv("GITHUB_TOKEN")

    def run_command(self, command: str) -> str:
        """Execute shell command safely.

        Args:
            command: Shell command string.

        Returns:
            Output string from command execution.
        """
        logger.info("Executing command: %s", command)
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            logger.warning("Command stderr output: %s", result.stderr.strip())
            return result.stderr.strip()
        return result.stdout.strip()

    def check_git_status(self) -> Dict[str, Any]:
        """Check working tree git status.

        Returns:
            Dict containing status summary and list of modified files.
        """
        status_output = self.run_command("git status --porcelain")
        changes = [
            line.strip() for line in status_output.split("\n") if line.strip()
        ]
        return {
            "has_changes": len(changes) > 0,
            "modified_count": len(changes),
            "file_changes": changes,
        }

    def sync_and_deploy(
        self,
        commit_message: str = (
            "feat: Day-3 CloudNative CI/CD & Container Security Pipeline"
        ),
        branch: str = "main",
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """Synchronize code changes and deploy to target GitHub repository.

        Args:
            commit_message: Message for git commit.
            branch: Target git branch name.
            dry_run: If True, simulates operations without pushing.

        Returns:
            Dict summarizing deployment result.
        """
        status = self.check_git_status()
        logger.info(
            "Working tree status: %d modified/untracked files.",
            status["modified_count"],
        )

        target_repo = self.repo_name
        logger.info("Target deployment repository: %s", target_repo)

        if dry_run:
            logger.info("[DRY RUN] Would execute: git add .")
            logger.info(
                "[DRY RUN] Would commit with message: '%s'", commit_message
            )
            logger.info(
                "[DRY RUN] Would sync & push to remote repo '%s' "
                "on branch '%s'",
                target_repo,
                branch,
            )
            return {
                "status": "SUCCESS",
                "mode": "DRY_RUN",
                "target_repository": target_repo,
                "branch": branch,
                "commit_message": commit_message,
                "modified_files": status["file_changes"],
                "message": (
                    "GitHub deployment simulation completed successfully."
                ),
            }

        # Stage changes
        self.run_command("git add .")

        # Commit changes if any exist
        if status["has_changes"]:
            commit_res = self.run_command(
                f'git commit -m "{commit_message}"'
            )
            logger.info("Commit output: %s", commit_res)
        else:
            logger.info("No uncommitted changes detected. Skipping commit.")

        # Push to remote branch
        push_res = self.run_command(f"git push origin {branch}")

        return {
            "status": "COMPLETED",
            "target_repository": target_repo,
            "branch": branch,
            "commit_message": commit_message,
            "output": push_res,
        }


def main() -> None:
    """CLI entrypoint for GitHub Deployer."""
    parser = argparse.ArgumentParser(
        description=(
            "Automated GitHub Repository Deployer "
            "for CloudNative-Ops-Day3"
        )
    )
    parser.add_argument(
        "--commit-msg",
        type=str,
        default=(
            "feat: Production CI/CD & Automated Container Security Pipeline"
        ),
        help="Git commit message.",
    )
    parser.add_argument(
        "--repo-name",
        type=str,
        default="devops-day3-cloudnative-pipeline",
        help="Target GitHub repository name.",
    )
    parser.add_argument(
        "--branch",
        type=str,
        default="main",
        help="Target remote branch.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Run deployment simulation without pushing live (default: True).",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Execute live git push to remote repository.",
    )

    args = parser.parse_args()
    deployer = GitHubDeployer(repo_name=args.repo_name)

    is_dry_run = not args.live
    result = deployer.sync_and_deploy(
        commit_message=args.commit_msg,
        branch=args.branch,
        dry_run=is_dry_run,
    )

    print("\n" + "=" * 60)
    print("GITHUB DEPLOYMENT SUMMARY")
    print("=" * 60)
    print(f"Status:       {result['status']}")
    print(f"Repository:   {result['target_repository']}")
    print(f"Branch:       {result['branch']}")
    print(f"Commit Msg:   {result['commit_message']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
