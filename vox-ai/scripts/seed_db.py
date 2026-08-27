"""Script to seed VOX-AI SQLite database with 1000 orders."""

import os
import sys

# Ensure vox-ai directory is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import init_db, seed_db  # noqa: E402


def main() -> None:
    """Main execution entry point to seed database."""
    print("Initializing SQLite database...")
    init_db()
    print("Seeding database with 1000 orders...")
    seed_db(num_orders=1000)
    print("Database seeding completed successfully.")


if __name__ == "__main__":
    main()
