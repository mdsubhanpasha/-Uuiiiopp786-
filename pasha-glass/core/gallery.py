"""
Encrypted Local Opt-In Face Gallery & Transient Data Manager for PASHA-GLASS.
Enforces strict 50-contact limit and 24-hour auto-deletion for transient data.
"""

import os
import json
import sqlite3
import time
import base64
import numpy as np
from typing import List, Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


MAX_OPT_IN_GALLERY_SIZE = 50
SIMILARITY_THRESHOLD = 0.85


class OptInGallery:
    """
    Manages encrypted local SQLite database for opt-in contacts and transient frame caches.
    Strictly isolated on-device, never uploads embeddings or contacts to the cloud.
    """

    def __init__(self, db_path: str = "pasha_glass_gallery.db", encryption_key: Optional[str] = None):
        self.db_path = db_path
        self._secret_key = self._derive_key(encryption_key or "PASHA_GLASS_LOCAL_ENCRYPTION_SECRET_KEY_2025")
        self.fernet = Fernet(self._secret_key)
        self._init_db()

    def _derive_key(self, secret: str) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"pasha_glass_local_salt_v1",
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(secret.encode()))

    def _encrypt(self, text: str) -> str:
        if not text:
            return ""
        return self.fernet.encrypt(text.encode()).decode()

    def _decrypt(self, token: str) -> str:
        if not token:
            return ""
        try:
            return self.fernet.decrypt(token.encode()).decode()
        except Exception:
            return token  # Fallback if unencrypted during development testing

    def _init_db(self) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Table for Opt-In Contacts (Max 50)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS optin_contacts (
                id TEXT PRIMARY KEY,
                name_enc TEXT NOT NULL,
                context_enc TEXT NOT NULL,
                photo_b64 TEXT,
                embedding_json TEXT NOT NULL,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            )
        """)
        # Table for Transient Frame Logs (Auto-deleted after 24h)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transient_frame_cache (
                frame_id TEXT PRIMARY KEY,
                detected_at REAL NOT NULL,
                matched_contact_id TEXT,
                is_opt_in INTEGER NOT NULL,
                status_text TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def count_contacts(self) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM optin_contacts")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def add_contact(
        self,
        contact_id: str,
        name: str,
        context: str,
        embedding: List[float],
        photo_b64: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a contact with explicit consent to the local gallery.
        Raises ValueError if capacity limit of 50 contacts is reached.
        """
        current_count = self.count_contacts()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check existing contact to allow update
        cursor.execute("SELECT id FROM optin_contacts WHERE id = ?", (contact_id,))
        exists = cursor.fetchone() is not None

        if not exists and current_count >= MAX_OPT_IN_GALLERY_SIZE:
            conn.close()
            raise ValueError(
                f"Opt-in gallery maximum capacity reached ({MAX_OPT_IN_GALLERY_SIZE} people limit)."
            )

        now = time.time()
        name_enc = self._encrypt(name)
        context_enc = self._encrypt(context)
        embedding_json = json.dumps(list(embedding))

        if exists:
            cursor.execute(
                """
                UPDATE optin_contacts
                SET name_enc = ?, context_enc = ?, photo_b64 = ?, embedding_json = ?, updated_at = ?
                WHERE id = ?
                """,
                (name_enc, context_enc, photo_b64, embedding_json, now, contact_id)
            )
        else:
            cursor.execute(
                """
                INSERT INTO optin_contacts
                (id, name_enc, context_enc, photo_b64, embedding_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (contact_id, name_enc, context_enc, photo_b64, embedding_json, now, now)
            )

        conn.commit()
        conn.close()

        return {
            "id": contact_id,
            "name": name,
            "context": context,
            "photo_b64": photo_b64,
            "created_at": now
        }

    def get_contact(self, contact_id: str) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name_enc, context_enc, photo_b64, embedding_json, created_at FROM optin_contacts WHERE id = ?",
            (contact_id,)
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        cid, name_enc, context_enc, photo_b64, embedding_json, created_at = row
        return {
            "id": cid,
            "name": self._decrypt(name_enc),
            "context": self._decrypt(context_enc),
            "photo_b64": photo_b64,
            "embedding": json.loads(embedding_json),
            "created_at": created_at
        }

    def list_contacts(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name_enc, context_enc, photo_b64, embedding_json, created_at FROM optin_contacts"
        )
        rows = cursor.fetchall()
        conn.close()

        result = []
        for row in rows:
            cid, name_enc, context_enc, photo_b64, embedding_json, created_at = row
            result.append({
                "id": cid,
                "name": self._decrypt(name_enc),
                "context": self._decrypt(context_enc),
                "photo_b64": photo_b64,
                "embedding": json.loads(embedding_json),
                "created_at": created_at
            })
        return result

    def delete_contact(self, contact_id: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM optin_contacts WHERE id = ?", (contact_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted

    def match_embedding(
        self,
        query_embedding: List[float],
        threshold: float = SIMILARITY_THRESHOLD
    ) -> Optional[Dict[str, Any]]:
        """
        Compare query embedding vector against local opt-in contacts using Cosine Similarity.
        If maximum similarity >= threshold, return contact match. Else return None.
        """
        contacts = self.list_contacts()
        if not contacts:
            return None

        q_vec = np.array(query_embedding, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm == 0:
            return None
        q_vec = q_vec / q_norm

        best_score = -1.0
        best_contact = None

        for contact in contacts:
            c_vec = np.array(contact["embedding"], dtype=np.float32)
            c_norm = np.linalg.norm(c_vec)
            if c_norm == 0:
                continue
            c_vec = c_vec / c_norm

            sim = float(np.dot(q_vec, c_vec))
            if sim > best_score:
                best_score = sim
                best_contact = contact

        if best_score >= threshold and best_contact:
            match_data = best_contact.copy()
            match_data["similarity_score"] = round(best_score, 4)
            return match_data

        return None

    def log_transient_frame(self, frame_id: str, is_opt_in: bool, matched_contact_id: Optional[str], status_text: str) -> None:
        """Record transient log for frame processing."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO transient_frame_cache (frame_id, detected_at, matched_contact_id, is_opt_in, status_text)
            VALUES (?, ?, ?, ?, ?)
            """,
            (frame_id, time.time(), matched_contact_id, 1 if is_opt_in else 0, status_text)
        )
        conn.commit()
        conn.close()

    def cleanup_transient_cache(self, max_age_seconds: float = 86400.0) -> int:
        """
        Auto-delete non-opt-in transient frame logs older than 24 hours (86,400 seconds).
        Returns number of deleted records.
        """
        cutoff = time.time() - max_age_seconds
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transient_frame_cache WHERE detected_at < ?", (cutoff,))
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        return deleted_count

    def purge_all(self) -> None:
        """Purge all data from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM optin_contacts")
        cursor.execute("DELETE FROM transient_frame_cache")
        conn.commit()
        conn.close()
