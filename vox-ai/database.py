"""VOX-AI Database Module.

Provides SQLite initialization, seeding with 1000 mock customer orders,
and function-calling interface for order lookups, appointment bookings, and human escalation.
"""

import os
import random
import sqlite3
import uuid
from typing import Any, Dict, List

DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "vox_ai.db")


def get_db_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Creates and returns a SQLite database connection with row factory configured.

    Args:
        db_path: Path to the SQLite database file.

    Returns:
        sqlite3.Connection: Database connection instance.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    """Initializes SQLite schema for orders and appointments tables.

    Args:
        db_path: Path to the SQLite database file.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            customer_name TEXT NOT NULL,
            item TEXT NOT NULL,
            status TEXT NOT NULL,
            shipping_address TEXT NOT NULL,
            estimated_delivery TEXT NOT NULL,
            price REAL NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            appointment_id TEXT PRIMARY KEY,
            customer_name TEXT NOT NULL,
            date TEXT NOT NULL,
            time_slot TEXT NOT NULL,
            service_type TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS escalations (
            escalation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            reason TEXT NOT NULL,
            sentiment_score REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def seed_db(db_path: str = DEFAULT_DB_PATH, num_orders: int = 1000) -> None:
    """Seeds the SQLite database with 1000 mock orders and initial appointment slots.

    Args:
        db_path: Path to the SQLite database file.
        num_orders: Number of mock orders to populate. Defaults to 1000.
    """
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM orders")
    count = cursor.fetchone()[0]

    if count >= num_orders:
        conn.close()
        return

    statuses = ["Processing", "Shipped", "Out for Delivery", "Delivered", "Delayed", "Cancelled"]
    items = [
        "Wireless Noise-Canceling Headphones", "Smart Fitness Watch", "Ultra-HD 4K Monitor",
        "Ergonomic Gaming Chair", "Mechanical RGB Keyboard", "Portable Bluetooth Speaker",
        "USB-C Docking Station", "HD Webcam 1080p", "Smart Home Voice Assistant", "Wireless Charging Pad"
    ]
    first_names = ["Alex", "Jordan", "Taylor", "Morgan", "Sam", "Chris", "Pat", "Riley", "Casey", "Avery"]
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones",
        "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"
    ]
    cities = [
        "New York, NY", "Los Angeles, CA", "Chicago, IL",
        "Houston, TX", "Phoenix, AZ", "Seattle, WA", "Austin, TX"
    ]

    random.seed(42)  # Deterministic seed for reproducible testing

    orders: List[tuple] = []

    # Ensure fixed test orders for explicit testing
    orders.append((
        "ORD-1001",
        "Alex Smith",
        "Wireless Noise-Canceling Headphones",
        "Shipped",
        "123 Tech Lane, Seattle, WA",
        "2026-03-30",
        199.99
    ))
    orders.append((
        "ORD-1002",
        "Jordan Johnson",
        "Smart Fitness Watch",
        "Out for Delivery",
        "456 Market St, San Francisco, CA",
        "2026-03-27",
        149.50
    ))
    orders.append((
        "ORD-1003",
        "Taylor Brown",
        "Ultra-HD 4K Monitor",
        "Delayed",
        "789 Pine Ave, Austin, TX",
        "2026-04-02",
        349.00
    ))

    start_num = len(orders) + 1001
    for i in range(start_num, start_num + num_orders - len(orders)):
        order_id = f"ORD-{i}"
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        item = random.choice(items)
        status = random.choice(statuses)
        city = random.choice(cities)
        street_num = random.randint(100, 999)
        address = f"{street_num} Main St, {city}"
        day = random.randint(28, 31)
        est_delivery = f"2026-03-{day:02d}"
        price = round(random.uniform(29.99, 499.99), 2)
        orders.append((order_id, name, item, status, address, est_delivery, price))

    cursor.executemany("""
        INSERT OR REPLACE INTO orders
        (order_id, customer_name, item, status, shipping_address, estimated_delivery, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, orders)

    conn.commit()
    conn.close()


def check_order(order_id: str, db_path: str = DEFAULT_DB_PATH) -> Dict[str, Any]:
    """Retrieves customer order status and tracking details by order ID.

    Args:
        order_id: Order identifier string (e.g. 'ORD-1001').
        db_path: Path to the SQLite database file.

    Returns:
        Dict[str, Any]: Order details dictionary or error status.
    """
    clean_id = order_id.strip().upper()
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM orders WHERE UPPER(order_id) = ?", (clean_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "found": True,
            "order_id": row["order_id"],
            "customer_name": row["customer_name"],
            "item": row["item"],
            "status": row["status"],
            "shipping_address": row["shipping_address"],
            "estimated_delivery": row["estimated_delivery"],
            "price": row["price"]
        }
    return {
        "found": False,
        "order_id": order_id,
        "message": f"Order {order_id} was not found in our database system."
    }


def book_appointment(
    customer_name: str,
    date: str,
    time_slot: str,
    service_type: str = "Support Consultation",
    db_path: str = DEFAULT_DB_PATH
) -> Dict[str, Any]:
    """Books a support appointment or callback for a customer.

    Args:
        customer_name: Name of the customer.
        date: Date string (e.g. '2026-03-30').
        time_slot: Time slot string (e.g. '10:00 AM').
        service_type: Type of support consultation.
        db_path: Path to the SQLite database file.

    Returns:
        Dict[str, Any]: Booking confirmation details.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    appointment_id = f"APT-{uuid.uuid4().hex[:8].upper()}"
    cursor.execute("""
        INSERT OR REPLACE INTO appointments (appointment_id, customer_name, date, time_slot, service_type, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (appointment_id, customer_name, date, time_slot, service_type, "Confirmed"))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "appointment_id": appointment_id,
        "customer_name": customer_name,
        "date": date,
        "time_slot": time_slot,
        "service_type": service_type,
        "status": "Confirmed",
        "message": f"Appointment successfully scheduled for {customer_name} on {date} at {time_slot}."
    }


def escalate_to_human(
    reason: str,
    sentiment_score: float = -0.8,
    db_path: str = DEFAULT_DB_PATH
) -> Dict[str, Any]:
    """Escalates the call session to a senior human support specialist.

    Args:
        reason: Explanation for escalation.
        sentiment_score: Negative sentiment score (-1.0 to 1.0).
        db_path: Path to the SQLite database file.

    Returns:
        Dict[str, Any]: Escalation receipt status.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO escalations (reason, sentiment_score, status)
        VALUES (?, ?, ?)
    """, (reason, sentiment_score, "Escalated to Tier-2 Support"))

    escalation_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {
        "escalated": True,
        "escalation_id": escalation_id,
        "reason": reason,
        "sentiment_score": sentiment_score,
        "target_queue": "Tier-2 Human Specialist Queue",
        "message": "Call successfully transferred to a live senior support specialist."
    }
