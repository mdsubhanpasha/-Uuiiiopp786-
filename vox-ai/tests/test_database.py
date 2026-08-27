"""Unit tests for VOX-AI Database Module."""

import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import (  # noqa: E402
    init_db, seed_db, check_order, book_appointment, escalate_to_human, get_db_connection
)


@pytest.fixture
def temp_db():
    """Fixture creating a temporary SQLite database for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    init_db(path)
    seed_db(path, num_orders=100)
    yield path
    if os.path.exists(path):
        os.remove(path)


def test_seed_db_count(temp_db):
    """Verifies database contains at least 100 seeded orders."""
    conn = get_db_connection(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM orders")
    count = cursor.fetchone()[0]
    conn.close()
    assert count >= 100


def test_check_order_found(temp_db):
    """Tests looking up existing order ORD-1001."""
    res = check_order("ORD-1001", temp_db)
    assert res["found"] is True
    assert res["order_id"] == "ORD-1001"
    assert res["customer_name"] == "Alex Smith"
    assert res["item"] == "Wireless Noise-Canceling Headphones"


def test_check_order_not_found(temp_db):
    """Tests looking up non-existent order ID."""
    res = check_order("ORD-999999", temp_db)
    assert res["found"] is False
    assert "not found" in res["message"]


def test_book_appointment(temp_db):
    """Tests creating a support appointment in DB."""
    res = book_appointment("Jordan Lee", "2026-04-10", "02:00 PM", "Technical Support", temp_db)
    assert res["success"] is True
    assert res["customer_name"] == "Jordan Lee"
    assert res["status"] == "Confirmed"
    assert res["appointment_id"].startswith("APT-")


def test_escalate_to_human(temp_db):
    """Tests escalating call session in DB."""
    res = escalate_to_human("Customer furious over delayed delivery", -0.9, temp_db)
    assert res["escalated"] is True
    assert res["target_queue"] == "Tier-2 Human Specialist Queue"
    assert res["escalation_id"] > 0
