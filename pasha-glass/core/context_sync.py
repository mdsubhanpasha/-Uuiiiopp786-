"""
Context Synchronization Adapter for PASHA-GLASS.
Syncs ONLY with user's own Calendar (Google Calendar) and CRM (HubSpot).
Strictly DOES NOT perform public social media scraping or external profiling.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional


class ContextSync:
    """
    Handles user calendar and CRM context resolution.
    Strictly isolated to user's authorized accounts.
    """

    def __init__(self):
        # Simulated user's private Google Calendar events
        self._user_calendar_events = [
            {
                "contact_name": "Daniel",
                "event_title": "Acme Corp AI Infra Sync",
                "start_time": datetime.now() + timedelta(minutes=10),
                "location": "Boardroom A / Glass HUD",
                "crm_notes": "Discuss Validator layer and edge deployment"
            },
            {
                "contact_name": "Sarah",
                "event_title": "CTO Architecture Review",
                "start_time": datetime.now() + timedelta(hours=2),
                "location": "Virtual",
                "crm_notes": "Review 20-agent LangGraph workflow performance"
            },
            {
                "contact_name": "Alex",
                "event_title": "Design System Touchpoint",
                "start_time": datetime.now() + timedelta(hours=4),
                "location": "Design Studio",
                "crm_notes": "Ray-Ban Meta Glasses HUD mock review"
            },
            {
                "contact_name": "Elena",
                "event_title": "Series B Investment Briefing",
                "start_time": datetime.now() + timedelta(days=1),
                "location": "Executive Suite",
                "crm_notes": "Privacy-first architecture whitepaper presentation"
            },
            {
                "contact_name": "Marcus",
                "event_title": "Security & Audit Sync",
                "start_time": datetime.now() + timedelta(days=2),
                "location": "Security Lab",
                "crm_notes": "BIPA & GDPR biometric consent verification"
            }
        ]

    def get_upcoming_meeting_for_contact(self, contact_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves upcoming calendar meeting for a recognized contact.
        """
        for event in self._user_calendar_events:
            if event["contact_name"].lower() in contact_name.lower():
                time_diff = event["start_time"] - datetime.now()
                minutes_left = int(time_diff.total_seconds() / 60)
                if minutes_left < 60:
                    time_str = f"in {minutes_left} mins"
                else:
                    hours_left = int(minutes_left / 60)
                    time_str = f"in {hours_left} hours"

                return {
                    "event_title": event["event_title"],
                    "time_str": time_str,
                    "location": event["location"],
                    "crm_notes": event["crm_notes"],
                    "hud_context_line": f"Meeting with {contact_name} {time_str} - {event['crm_notes']}"
                }
        return None

    def resolve_augmented_context(self, contact_name: str, base_context: str) -> str:
        """
        Combines base local context notes with real-time calendar context.
        """
        meeting = self.get_upcoming_meeting_for_contact(contact_name)
        if meeting:
            return f"{base_context} | {meeting['hud_context_line']}"
        return f"{base_context} | No immediate meeting scheduled"
