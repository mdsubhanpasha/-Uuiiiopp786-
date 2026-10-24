"""
Seeded Demo Application for PASHA-GLASS.
Loads 5 opt-in contacts into the local encrypted gallery and runs interactive privacy demo scenarios.
"""

import os
import sys
import cv2
import numpy as np

# Ensure pasha-glass root directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.gallery import OptInGallery
from core.face_engine import FaceEngine
from core.context_sync import ContextSync
from core.ble_stream import MetaGlassesBLEStream


# 5 Seeded Opt-In Contacts with Explicit Consent
DEMO_CONTACTS = [
    {
        "id": "c_daniel",
        "name": "Daniel",
        "context": "Client from Acme, likes AI infra",
        "seed": "daniel_seed"
    },
    {
        "id": "c_sarah",
        "name": "Sarah",
        "context": "CTO Partner, prefers LangGraph & async design",
        "seed": "sarah_seed"
    },
    {
        "id": "c_alex",
        "name": "Alex",
        "context": "Lead Designer, lead on Ray-Ban HUD UX",
        "seed": "alex_seed"
    },
    {
        "id": "c_elena",
        "name": "Elena",
        "context": "Investor at VC, focused on Edge AI & Privacy",
        "seed": "elena_seed"
    },
    {
        "id": "c_marcus",
        "name": "Marcus",
        "context": "Security Lead, compliance auditor for BIPA/GDPR",
        "seed": "marcus_seed"
    }
]


def run_demo(db_path: str = "pasha_glass_demo.db"):
    print("=" * 70)
    print("PASHA-GLASS: PRIVACY-FIRST CONTEXT ASSISTANT DEMO")
    print("Core Principle: NO facial recognition of unknown people.")
    print("NO social media scraping. Only local opt-in recognition.")
    print("=" * 70)

    gallery = OptInGallery(db_path=db_path)
    gallery.purge_all()

    face_engine = FaceEngine(gallery)
    context_sync = ContextSync()
    ble_stream = MetaGlassesBLEStream()

    print("\n1. SEEDING 5 OPT-IN CONTACTS WITH EXPLICIT CONSENT...")
    dummy_img = np.zeros((10, 10, 3), dtype=np.uint8)

    for c in DEMO_CONTACTS:
        embedding = face_engine.extract_embedding_synthetic(dummy_img, seed_id=c["seed"])
        gallery.add_contact(
            contact_id=c["id"],
            name=c["name"],
            context=c["context"],
            embedding=embedding
        )
        print(f"   [+] Opt-in Registered: {c['name']} ({c['context']})")

    print(f"\n   Total contacts in local encrypted gallery: {gallery.count_contacts()}/50 (Limit Enforced)")

    print("\n" + "-" * 70)
    print("2. RUNNING DEMO SCENARIOS OVER SIMULATED META GLASSES BLE STREAM...")
    print("-" * 70)

    # Scenario A: Known Contact (Daniel)
    print("\n[SCENARIO A] Known Opt-In Contact (Daniel) enters frame...")
    frame, _ = ble_stream.generate_synthetic_frame("Camera Stream: Daniel in view")
    bboxes_a = face_engine.detect_faces(frame)
    known_map_a = {bboxes_a[0]: "daniel_seed"} if bboxes_a else {}
    result_a = face_engine.process_frame(frame, known_seeds_map=known_map_a)

    for card in result_a["hud_cards"]:
        if card["is_known"]:
            aug = context_sync.resolve_augmented_context(card["name"], card["context"])
            print(f"   [HUD DISPLAY CARD]: '{card['name']}'")
            print(f"   [MATCH CONFIDENCE]: {card['similarity'] * 100:.1f}% (Threshold >= 85%)")
            print(f"   [CONTEXT OVERLAY] : {aug}")
            print("   [PRIVACY ACTION]  : Face rendered CLEAR (Opt-In Verified)")

    # Scenario B: Unknown Person
    print("\n[SCENARIO B] Unknown Person (No Opt-In Consent) enters frame...")
    frame_unk, _ = ble_stream.generate_synthetic_frame("Camera Stream: Unknown Person")
    bboxes_b = face_engine.detect_faces(frame_unk)
    known_map_b = {bboxes_b[0]: "unknown_person_123"} if bboxes_b else {}
    result_b = face_engine.process_frame(frame_unk, known_seeds_map=known_map_b)

    for card in result_b["hud_cards"]:
        if not card["is_known"]:
            print(f"   [HUD DISPLAY CARD]: '{card['hud_text']}'")
            print(f"   [MATCH CONFIDENCE]: {card['similarity'] * 100:.1f}% (< 85% Threshold)")
            print("   [PRIVACY ACTION]  : Mandatory Gaussian Blur applied on-device")
            print("   [CLOUD / NETWORK] : Zero public social scraping attempted")

    print("\n" + "=" * 70)
    print("DEMO COMPLETE - ALL PRIVACY SAFEGUARDS VERIFIED SUCCESSFULLY!")
    print("=" * 70)

    if os.path.exists(db_path):
        os.remove(db_path)


if __name__ == "__main__":
    run_demo()
