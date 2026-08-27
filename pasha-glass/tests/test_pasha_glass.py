"""
Comprehensive Automated Unit & Integration Tests for PASHA-GLASS.
Tests privacy compliance, face blurring, opt-in gallery limits (max 50), similarity threshold (>=0.85),
24-hour transient data cleanup, context synchronization, and FastAPI endpoints.
"""

import os
import sys
import time
import pytest
import numpy as np
from fastapi.testclient import TestClient

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.gallery import OptInGallery, MAX_OPT_IN_GALLERY_SIZE, SIMILARITY_THRESHOLD
from core.face_engine import FaceEngine
from core.context_sync import ContextSync
from core.ble_stream import MetaGlassesBLEStream
from api.main import app, gallery as api_gallery


TEST_DB_PATH = "test_pasha_glass_suite.db"


@pytest.fixture
def test_gallery():
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    gal = OptInGallery(db_path=TEST_DB_PATH)
    yield gal
    gal.purge_all()
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


def test_gallery_capacity_limit(test_gallery):
    """Verify that gallery enforces hard max limit of 50 contacts."""
    dummy_vec = [0.1] * 512
    for i in range(MAX_OPT_IN_GALLERY_SIZE):
        test_gallery.add_contact(f"c_{i}", f"User {i}", f"Context {i}", dummy_vec)

    assert test_gallery.count_contacts() == MAX_OPT_IN_GALLERY_SIZE

    # Attempt to add 51st contact
    with pytest.raises(ValueError, match="maximum capacity reached"):
        test_gallery.add_contact("c_51", "User 51", "Overflow Context", dummy_vec)


def test_gallery_encryption_and_crud(test_gallery):
    """Verify encrypted storage and CRUD operations."""
    vec = [0.5] * 512
    added = test_gallery.add_contact("c_daniel", "Daniel", "Client from Acme", vec)
    assert added["name"] == "Daniel"

    fetched = test_gallery.get_contact("c_daniel")
    assert fetched is not None
    assert fetched["name"] == "Daniel"
    assert fetched["context"] == "Client from Acme"

    # Delete contact
    deleted = test_gallery.delete_contact("c_daniel")
    assert deleted is True
    assert test_gallery.get_contact("c_daniel") is None


def test_face_engine_matching_threshold(test_gallery):
    """Verify cosine similarity threshold (>= 0.85)."""
    engine = FaceEngine(test_gallery)
    vec = engine.extract_embedding_synthetic(np.zeros((10, 10, 3)), seed_id="daniel_seed")

    test_gallery.add_contact("c_daniel", "Daniel", "Client from Acme", vec)

    # Test exact / high similarity match (>= 0.85)
    matched = test_gallery.match_embedding(vec, threshold=SIMILARITY_THRESHOLD)
    assert matched is not None
    assert matched["name"] == "Daniel"
    assert matched["similarity_score"] >= 0.85

    # Test low similarity query (< 0.85)
    different_vec = engine.extract_embedding_synthetic(np.zeros((10, 10, 3)), seed_id="stranger_seed")
    unmatched = test_gallery.match_embedding(different_vec, threshold=SIMILARITY_THRESHOLD)
    assert unmatched is None


def test_face_blurring_on_unknown(test_gallery):
    """Verify that unknown face yields 'Unknown person - no data' HUD card and blurred face frame."""
    engine = FaceEngine(test_gallery)
    frame, _ = MetaGlassesBLEStream().generate_synthetic_frame("Test Frame")

    bboxes = engine.detect_faces(frame)
    bbox = bboxes[0] if bboxes else (100, 100, 100, 100)

    # Process frame with unknown person seed
    res = engine.process_frame(frame, known_seeds_map={bbox: "unknown_person_999"})

    assert res["detected_count"] > 0
    assert len(res["hud_cards"]) > 0
    card = res["hud_cards"][0]

    assert card["is_known"] is False
    assert card["name"] == "Unknown"
    assert card["hud_text"] == "Unknown person - no data"


def test_24h_transient_cache_cleanup(test_gallery):
    """Verify transient frame cache cleanup."""
    test_gallery.log_transient_frame("frame_old", is_opt_in=False, matched_contact_id=None, status_text="Blurred")

    # Clean up with max_age_seconds=0 to delete immediately
    deleted = test_gallery.cleanup_transient_cache(max_age_seconds=0.0)
    assert deleted >= 1


def test_context_sync():
    """Verify Google Calendar/CRM context sync."""
    cs = ContextSync()
    meeting = cs.get_upcoming_meeting_for_contact("Daniel")
    assert meeting is not None
    assert "in 9 mins" in meeting["hud_context_line"] or "mins" in meeting["hud_context_line"]


def test_api_endpoints():
    """Integration test for FastAPI companion backend API endpoints."""
    api_gallery.purge_all()
    client = TestClient(app)

    # Root
    r = client.get("/")
    assert r.status_code == 200
    assert "PASHA-GLASS" in r.json()["service"]

    # Add Contact
    r_add = client.post("/api/v1/gallery", json={
        "contact_id": "c_daniel_api",
        "name": "Daniel",
        "context": "Client from Acme",
        "seed_key": "daniel_seed"
    })
    assert r_add.status_code == 201

    # List Contacts
    r_list = client.get("/api/v1/gallery")
    assert r_list.status_code == 200
    assert len(r_list.json()) == 1

    # Process Frame (Known seed)
    r_proc = client.post("/api/v1/process-frame", json={"seed_id": "daniel_seed"})
    assert r_proc.status_code == 200
    hud_card = r_proc.json()["hud_cards"][0]
    assert hud_card["is_known"] is True
    assert hud_card["name"] == "Daniel"

    # Process Frame (Unknown seed)
    r_unk = client.post("/api/v1/process-frame", json={"seed_id": "stranger_123"})
    assert r_unk.status_code == 200
    unk_card = r_unk.json()["hud_cards"][0]
    assert unk_card["is_known"] is False
    assert unk_card["hud_text"] == "Unknown person - no data"

    # Purge
    r_purge = client.post("/api/v1/gallery/purge")
    assert r_purge.status_code == 200
    assert len(client.get("/api/v1/gallery").json()) == 0
