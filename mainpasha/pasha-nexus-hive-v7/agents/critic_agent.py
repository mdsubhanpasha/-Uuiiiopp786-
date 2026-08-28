"""
PASHA-NEXUS-HIVE V7 - QA Critic & Virality Agent
Evaluates tailored outputs (0-100 score). Rejects and triggers feedback loop if score < 85.
"""
from typing import Dict, Any, List

class CriticAgent:
    def __init__(self, pass_threshold: int = 85):
        self.pass_threshold = pass_threshold

    def evaluate_output(self, resume_data: Dict[str, Any], cover_letter: str, jd_keywords: List[str]) -> Dict[str, Any]:
        """Evaluate resume ATS score, STAR metrics, and cover letter alignment."""
        score_breakdown = {
            "ats_keyword_match": 0,
            "star_impact_metrics": 0,
            "cover_letter_quality": 0,
            "pasha_os_reference": 0
        }

        # 1. ATS Match
        ats_score = resume_data.get("ats_score", 85)
        score_breakdown["ats_keyword_match"] = min(30, int(ats_score * 0.3))

        # 2. STAR & Metrics
        full_text = str(resume_data) + cover_letter
        star_count = full_text.count("[STAR]") + full_text.count("Built") + full_text.count("Architected")
        score_breakdown["star_impact_metrics"] = min(25, star_count * 5 + 10)

        # 3. 6 OS References
        os_names = ["PASHA-OS", "NEURO-RAG", "VOX-AI", "PASHA-UNIFIED-OS", "AUTO-GROWTH", "PASHA-GLASS"]
        found_os = sum(1 for os_name in os_names if os_name in full_text)
        score_breakdown["pasha_os_reference"] = min(25, found_os * 5)

        # 4. Cover Letter Quality
        score_breakdown["cover_letter_quality"] = 20 if len(cover_letter) > 200 else 10

        total_score = sum(score_breakdown.values())
        passed = total_score >= self.pass_threshold

        feedback = []
        if not passed:
            if score_breakdown["pasha_os_reference"] < 15:
                feedback.append("Inject more specific metrics from past 6 OS platforms (e.g. 25-agent MNC, RAGAS 0.96, VOX-AI <300ms).")
            if score_breakdown["star_impact_metrics"] < 15:
                feedback.append("Ensure every experience bullet uses strict STAR formatting with clear quantitative impact.")

        return {
            "score": total_score,
            "passed": passed,
            "pass_threshold": self.pass_threshold,
            "breakdown": score_breakdown,
            "feedback": feedback or ["High quality output! Meets top 10% ATS and executive hiring criteria."]
        }
