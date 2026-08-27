"""VOX-AI Sentiment Analysis & Auto-Escalation Engine.

Detects user emotional state, calculates sentiment scores, and flags angry/frustrated
users for immediate tone adaptation and human agent escalation.
"""

from typing import Dict, Any

ANGRY_KEYWORDS = [
    "angry", "furious", "terrible", "horrible", "ridiculous", "unacceptable",
    "worst", "scam", "sucks", "disaster", "hate", "waste of time", "pissed",
    "stolen", "lawyer", "lawsuit", "sue", "manager", "supervisor", "human",
    "real person", "agent", "refund immediately", "cancel everything"
]

POSITIVE_KEYWORDS = [
    "thank", "thanks", "great", "awesome", "excellent", "wonderful", "perfect",
    "helpful", "good", "happy", "appreciate", "love"
]


def analyze_sentiment(text: str) -> Dict[str, Any]:
    """Analyzes text for sentiment polarity and escalation condition.

    Args:
        text: User spoken input transcribed from speech.

    Returns:
        Dict[str, Any]: Sentiment analysis result containing score, label,
                        and escalation flag.
    """
    if not text:
        return {
            "score": 0.0,
            "label": "neutral",
            "is_angry": False,
            "should_escalate": False,
            "reason": None
        }

    lowered = text.lower()

    # Count matching keyword frequencies
    angry_matches = [word for word in ANGRY_KEYWORDS if word in lowered]
    positive_matches = [word for word in POSITIVE_KEYWORDS if word in lowered]

    # Check for all-caps shouting or multiple exclamation marks
    exclamation_count = text.count("!")
    is_shouting = text.isupper() and len(text) > 5

    # Base score calculation (-1.0 to 1.0)
    score = 0.0
    if angry_matches:
        score -= min(0.4 * len(angry_matches), 0.9)
    if positive_matches:
        score += min(0.3 * len(positive_matches), 0.8)

    if is_shouting:
        score -= 0.3
    if exclamation_count > 1 and score <= 0:
        score -= 0.2

    score = max(-1.0, min(1.0, score))

    is_angry = score <= -0.5 or len(angry_matches) >= 2 or is_shouting
    should_escalate = is_angry or any(
        kw in lowered for kw in ["manager", "supervisor", "human", "real person", "transfer me", "speak to someone"]
    )

    if is_angry:
        label = "angry"
    elif score < -0.2:
        label = "negative"
    elif score > 0.2:
        label = "positive"
    else:
        label = "neutral"

    reason = None
    if should_escalate:
        if angry_matches:
            reason = f"High customer frustration detected (keywords: {', '.join(angry_matches[:3])})"
        elif is_shouting:
            reason = "Customer shouting / elevated tone detected"
        else:
            reason = "Customer explicitly requested human escalation"

    return {
        "score": round(score, 2),
        "label": label,
        "is_angry": is_angry,
        "should_escalate": should_escalate,
        "reason": reason
    }
