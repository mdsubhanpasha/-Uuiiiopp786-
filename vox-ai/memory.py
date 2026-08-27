"""VOX-AI Memory Module.

Provides conversation history and sentiment context persistence using Redis,
with automatic graceful fallback to in-memory storage.
"""

import json
import os
from typing import Dict, List, Optional

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class ConversationMemory:
    """Manages conversation context and sentiment state across voice call turns."""

    def __init__(self, session_id: str, redis_url: Optional[str] = None) -> None:
        """Initializes memory manager for a specific call session.

        Args:
            session_id: Unique call session identifier.
            redis_url: Connection URL for Redis server. Defaults to REDIS_URL env var or localhost.
        """
        self.session_id = session_id
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis_client = None
        self.in_memory_store: List[Dict[str, str]] = []
        self.in_memory_sentiment: List[float] = []

        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.Redis.from_url(self.redis_url, decode_responses=True, socket_timeout=1.0)
                self.redis_client.ping()
            except Exception:
                self.redis_client = None

    def add_message(self, role: str, content: str) -> None:
        """Appends a message to session history.

        Args:
            role: 'user', 'assistant', or 'system'.
            content: Message text content.
        """
        msg = {"role": role, "content": content}
        if self.redis_client:
            try:
                key = f"voxai:session:{self.session_id}:history"
                self.redis_client.rpush(key, json.dumps(msg))
                self.redis_client.expire(key, 86400)  # 24 hour TTL
                return
            except Exception:
                self.redis_client = None

        self.in_memory_store.append(msg)

    def get_history(self) -> List[Dict[str, str]]:
        """Retrieves full conversation history.

        Returns:
            List[Dict[str, str]]: List of role-content message objects.
        """
        if self.redis_client:
            try:
                key = f"voxai:session:{self.session_id}:history"
                items = self.redis_client.lrange(key, 0, -1)
                return [json.loads(item) for item in items]
            except Exception:
                self.redis_client = None

        return list(self.in_memory_store)

    def add_sentiment_score(self, score: float) -> None:
        """Records a sentiment score for the current session turn.

        Args:
            score: Sentiment score from -1.0 (very negative/angry) to +1.0 (very positive).
        """
        if self.redis_client:
            try:
                key = f"voxai:session:{self.session_id}:sentiment"
                self.redis_client.rpush(key, str(score))
                self.redis_client.expire(key, 86400)
                return
            except Exception:
                self.redis_client = None

        self.in_memory_sentiment.append(score)

    def get_average_sentiment(self) -> float:
        """Calculates average sentiment score for session.

        Returns:
            float: Average score (-1.0 to 1.0).
        """
        if self.redis_client:
            try:
                key = f"voxai:session:{self.session_id}:sentiment"
                items = self.redis_client.lrange(key, 0, -1)
                if items:
                    scores = [float(x) for x in items]
                    return sum(scores) / len(scores)
            except Exception:
                self.redis_client = None

        if self.in_memory_sentiment:
            return sum(self.in_memory_sentiment) / len(self.in_memory_sentiment)
        return 0.0

    def clear(self) -> None:
        """Clears memory for this session."""
        if self.redis_client:
            try:
                self.redis_client.delete(
                    f"voxai:session:{self.session_id}:history",
                    f"voxai:session:{self.session_id}:sentiment"
                )
            except Exception:
                pass
        self.in_memory_store.clear()
        self.in_memory_sentiment.clear()
