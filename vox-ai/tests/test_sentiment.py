"""Unit tests for VOX-AI Sentiment Analysis Module."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentiment import analyze_sentiment  # noqa: E402


def test_neutral_sentiment():
    """Tests neutral customer query."""
    res = analyze_sentiment("What is the status of my order ORD-1001?")
    assert res["is_angry"] is False
    assert res["should_escalate"] is False
    assert res["label"] in ["neutral", "positive"]


def test_positive_sentiment():
    """Tests positive customer feedback."""
    res = analyze_sentiment("Thank you so much! That was awesome and extremely helpful.")
    assert res["score"] > 0
    assert res["label"] == "positive"
    assert res["should_escalate"] is False


def test_angry_sentiment():
    """Tests angry customer query triggering auto-escalation."""
    res = analyze_sentiment(
        "I am furious! Your service is terrible and ridiculous! Transfer me to a human manager right now!"
    )
    assert res["is_angry"] is True
    assert res["should_escalate"] is True
    assert res["label"] == "angry"
    assert "frustration" in res["reason"] or "human" in res["reason"]


def test_explicit_human_request():
    """Tests explicit request to speak with a real person."""
    res = analyze_sentiment("Can I speak to a real person please?")
    assert res["should_escalate"] is True
    assert res["reason"] is not None
