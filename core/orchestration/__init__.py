"""Auron Brain & Pasha Orchestration Module."""

try:
    from core.orchestration.auron_brain import AuronBrain
except ImportError as e:
    AuronBrain = None
    print(f"AuronBrain not available: {e}")

from core.orchestration_legacy import PashaOrchestrator

__all__ = ["AuronBrain", "PashaOrchestrator"]
