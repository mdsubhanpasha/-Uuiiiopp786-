"""
Application Package Generator for JobSentinel.
Tailors base resume (highlighting ChurnGuard zero-trust project), generates custom cover letter,
creates hiring manager outreach message, and outputs to /applications/{date}/{company}_{role}/.
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional
from job_sentinel.config import APPLICATIONS_DIR
from job_sentinel.discovery import JobPosting


BASE_RESUME_TEMPLATE = """# Candidate Resume
**Email**: candidate@example.com | **Location**: Europe / Remote | **LinkedIn**: linkedin.com/in/candidate

## Professional Summary
Results-driven Business & Product Analyst with 3+ years of experience delivering AI automation, financial workflow optimization, and SQL data engineering solutions in banking and tech environments.

## Core Accomplishments & Projects

### ChurnGuard & Autonomous Analytics Platform (Lead Analyst)
- [BULLET_1] Engineered zero-trust customer churn prediction pipeline with 94.2% precision using SQL and Python.
- [BULLET_2] Optimized financial data structures to accelerate reporting throughput by 40% across multi-currency ledgers.
- [BULLET_3] Designed executive decision-making dashboards and automated alert workflows reducing operational overhead.

## Technical Skills
- **Languages & Tools**: SQL, Python, Data Structures, AI Automation, Prompt Engineering
- **Domain Expertise**: Finance, Treasury Optimization, Operations, Risk Analysis
"""


class ApplicationPackageGenerator:
    """Generates tailored application materials for high-scoring job positions."""

    def __init__(self, base_dir: str = APPLICATIONS_DIR):
        self.base_dir = base_dir

    def sanitize_path_component(self, text: str) -> str:
        """Sanitizes company or role strings for safe filesystem folder naming."""
        clean = re.sub(r"[^\w\s-]", "", text).strip().replace(" ", "_")
        return clean.lower()[:30]

    def tailor_resume_bullets(self, job: JobPosting) -> List[str]:
        """
        Modifies 3 bullet points in the ChurnGuard project section
        to match job description keywords.
        """
        top_skills = job.skills[:3] if job.skills else ["SQL", "AI Automation", "Finance"]
        bullet_1 = (
            f"Engineered zero-trust customer churn prediction and {top_skills[0]} pipeline "
            f"for {job.company}, achieving 94.2% precision and aligning with {job.title} metrics."
        )

        second_skill = top_skills[1] if len(top_skills) > 1 else "data structures"
        bullet_2 = (
            f"Optimized {second_skill} and automated financial workflows, accelerating "
            f"throughput by 45% and solving key operational hurdles identified in {job.company}'s operations."
        )

        third_skill = top_skills[2] if len(top_skills) > 2 else "AI tools"
        bullet_3 = (
            f"Implemented automated {third_skill} decision frameworks and executive telemetry, "
            f"directly streamlining business analysis workflows for 2-5 year experience SLA requirements."
        )

        return [bullet_1, bullet_2, bullet_3]

    def generate_tailored_resume(self, job: JobPosting, tailored_bullets: List[str]) -> str:
        """Generates tailored Markdown resume."""
        resume = BASE_RESUME_TEMPLATE
        resume = resume.replace("[BULLET_1]", tailored_bullets[0])
        resume = resume.replace("[BULLET_2]", tailored_bullets[1])
        resume = resume.replace("[BULLET_3]", tailored_bullets[2])
        return resume

    def generate_cover_letter(self, job: JobPosting, fit_reason: str) -> str:
        """Generates custom cover letter addressing specific business needs."""
        date_str = datetime.now().strftime("%B %d, %Y")
        business_need = "treasury & financial workflow optimization" if "finance" in job.description.lower() else "AI automation and analytical decision support"

        cover_letter = f"""{date_str}

Hiring Manager / Talent Acquisition
{job.company}
{job.location}

RE: Application for {job.title} Position

Dear Hiring Manager,

I am writing to express my enthusiastic interest in the {job.title} role at {job.company}. Having followed {job.company}'s market initiatives, I am eager to apply my experience in SQL, data structures, and AI-driven automation to solve your operational priorities—specifically regarding {business_need}.

In my previous project work (including the ChurnGuard platform), I built zero-trust data pipelines and automated analysis systems that reduced manual processing overhead by 40%. My background directly satisfies your requirements for {job.experience_years} of experience and expertise in {', '.join(job.skills[:4])}.

Key highlights I bring to {job.company}:
1. Proven expertise in SQL & Python data modeling for high-accuracy decision support.
2. Direct experience optimizing domain workflows ({fit_reason}).
3. A zero-trust engineering mindset prioritizing security, accuracy, and operational efficiency.

I look forward to discussing how my skills in {job.title} can drive immediate value for {job.company}.

Sincerely,

Candidate Name
Business & Product Analyst
"""
        return cover_letter

    def generate_outreach_message(self, job: JobPosting) -> str:
        """Generates hiring manager outreach message for LinkedIn message/email."""
        return (
            f"Hi [Hiring Manager / Recruiter Name],\n\n"
            f"I recently noticed the {job.title} opening at {job.company} and wanted to reach out directly. "
            f"My background in SQL, AI automation, and financial process optimization aligns closely with "
            f"the team's work on {job.skills[0] if job.skills else 'analytics'}.\n\n"
            f"I have prepared a tailored package (resume + cover letter) highlighting relevant ChurnGuard project "
            f"outcomes. Would love to connect briefly!\n\n"
            f"Best regards,\nCandidate"
        )

    def create_package(
        self,
        job: JobPosting,
        score: float,
        breakdown: Dict[str, Any],
        date_str: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Creates full application package and saves to /applications/{date}/{company}_{role}/.
        """
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")

        company_clean = self.sanitize_path_component(job.company)
        role_clean = self.sanitize_path_component(job.title)
        package_folder = os.path.join(self.base_dir, date_str, f"{company_clean}_{role_clean}")

        os.makedirs(package_folder, exist_ok=True)

        # 1. Tailored Resume
        bullets = self.tailor_resume_bullets(job)
        tailored_resume = self.generate_tailored_resume(job, bullets)
        resume_path = os.path.join(package_folder, "resume.md")
        with open(resume_path, "w", encoding="utf-8") as f:
            f.write(tailored_resume)

        # 2. Cover Letter
        cover_letter = self.generate_cover_letter(job, breakdown.get("fit_reason", ""))
        cover_letter_path = os.path.join(package_folder, "cover_letter.md")
        with open(cover_letter_path, "w", encoding="utf-8") as f:
            f.write(cover_letter)

        # 3. Hiring Manager Outreach Message
        outreach_msg = self.generate_outreach_message(job)
        outreach_path = os.path.join(package_folder, "outreach_message.txt")
        with open(outreach_path, "w", encoding="utf-8") as f:
            f.write(outreach_msg)

        # 4. Package Metadata
        metadata = {
            "date": date_str,
            "job_id": job.job_id,
            "company": job.company,
            "title": job.title,
            "score": score,
            "breakdown": breakdown,
            "job_url": job.job_url,
            "apply_type": job.apply_type,
            "package_folder": package_folder,
            "status": "DRAFTED_PENDING_APPROVAL",
            "modified_bullets": bullets,
        }
        metadata_path = os.path.join(package_folder, "metadata.json")
        with open(metadata_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(metadata, indent=2))

        return metadata
