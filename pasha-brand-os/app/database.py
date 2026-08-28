import os
import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from loguru import logger

DEFAULT_DB_PATH = os.getenv("DATABASE_PATH", "app/pasha_brand_os.db")

def get_db_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: str = DEFAULT_DB_PATH):
    """Initializes SQLite tables for PASHA-UNIFIED-OS."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    # News table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT,
        source_url TEXT UNIQUE,
        category TEXT,
        relevance_score REAL,
        published_at TEXT,
        fetched_at TEXT NOT NULL
    )
    """)

    # Posts table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT NOT NULL,
        angle TEXT NOT NULL,
        variant_type TEXT,
        hook TEXT,
        problem TEXT,
        insight TEXT,
        cta TEXT,
        full_text TEXT NOT NULL,
        hashtags TEXT,
        image_url TEXT,
        image_prompt TEXT,
        virality_score INTEGER,
        predicted_views TEXT,
        feedback TEXT,
        status TEXT DEFAULT 'pending_approval',
        scheduled_time TEXT,
        linkedin_post_id TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)

    # Analytics table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analytics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER,
        linkedin_post_id TEXT,
        views INTEGER DEFAULT 0,
        likes INTEGER DEFAULT 0,
        comments INTEGER DEFAULT 0,
        shares INTEGER DEFAULT 0,
        follower_delta INTEGER DEFAULT 0,
        dm_leads INTEGER DEFAULT 0,
        scraped_at TEXT NOT NULL,
        FOREIGN KEY (post_id) REFERENCES posts (id)
    )
    """)

    # Auto-engagement comments table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS auto_comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        target_post_id TEXT,
        target_author TEXT,
        target_url TEXT,
        hashtag TEXT,
        comment_text TEXT NOT NULL,
        posted_at TEXT NOT NULL,
        status TEXT DEFAULT 'posted'
    )
    """)

    # Competitor hooks table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS competitor_hooks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        influencer_name TEXT NOT NULL,
        original_post TEXT NOT NULL,
        hook_type TEXT,
        hook_text TEXT NOT NULL,
        likes INTEGER DEFAULT 0,
        scraped_at TEXT NOT NULL
    )
    """)

    # Settings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()
    logger.info("Database initialized successfully at {}", db_path)

# Helper functions for database operations

def save_news_articles(articles: List[Dict[str, Any]], db_path: str = DEFAULT_DB_PATH) -> int:
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    saved = 0
    now = datetime.now(timezone.utc).isoformat()
    for item in articles:
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO news (title, content, source_url, category, relevance_score, published_at, fetched_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                item.get("title", ""),
                item.get("content", ""),
                item.get("source_url", ""),
                item.get("category", "AI"),
                item.get("relevance_score", 50.0),
                item.get("published_at", now),
                now
            ))
            saved += 1
        except Exception as e:
            logger.warning("Error saving news article {}: {}", item.get("source_url"), e)
    conn.commit()
    conn.close()
    return saved

def get_top_news(limit: int = 20, db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM news ORDER BY relevance_score DESC, fetched_at DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def insert_post(post_data: Dict[str, Any], db_path: str = DEFAULT_DB_PATH) -> int:
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    cursor.execute("""
        INSERT INTO posts (topic, angle, variant_type, hook, problem, insight, cta, full_text, hashtags, image_url, image_prompt, virality_score, predicted_views, feedback, status, scheduled_time, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        post_data.get("topic", ""),
        post_data.get("angle", ""),
        post_data.get("variant_type", "Story"),
        post_data.get("hook", ""),
        post_data.get("problem", ""),
        post_data.get("insight", ""),
        post_data.get("cta", ""),
        post_data.get("full_text", ""),
        post_data.get("hashtags", ""),
        post_data.get("image_url", ""),
        post_data.get("image_prompt", ""),
        post_data.get("virality_score", 0),
        post_data.get("predicted_views", "1k-3k views"),
        post_data.get("feedback", ""),
        post_data.get("status", "pending_approval"),
        post_data.get("scheduled_time"),
        now,
        now
    ))
    post_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return post_id

def update_post_status(post_id: int, status: str, scheduled_time: Optional[str] = None, linkedin_post_id: Optional[str] = None, db_path: str = DEFAULT_DB_PATH):
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    if scheduled_time and linkedin_post_id:
        cursor.execute("UPDATE posts SET status = ?, scheduled_time = ?, linkedin_post_id = ?, updated_at = ? WHERE id = ?",
                       (status, scheduled_time, linkedin_post_id, now, post_id))
    elif scheduled_time:
        cursor.execute("UPDATE posts SET status = ?, scheduled_time = ?, updated_at = ? WHERE id = ?",
                       (status, scheduled_time, now, post_id))
    elif linkedin_post_id:
        cursor.execute("UPDATE posts SET status = ?, linkedin_post_id = ?, updated_at = ? WHERE id = ?",
                       (status, linkedin_post_id, now, post_id))
    else:
        cursor.execute("UPDATE posts SET status = ?, updated_at = ? WHERE id = ?",
                       (status, now, post_id))
    conn.commit()
    conn.close()

def update_post_content(post_id: int, full_text: Optional[str] = None, image_url: Optional[str] = None, hook: Optional[str] = None, feedback: Optional[str] = None, db_path: str = DEFAULT_DB_PATH):
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    fields = []
    params = []
    if full_text:
        fields.append("full_text = ?")
        params.append(full_text)
    if image_url:
        fields.append("image_url = ?")
        params.append(image_url)
    if hook:
        fields.append("hook = ?")
        params.append(hook)
    if feedback is not None:
        fields.append("feedback = ?")
        params.append(feedback)

    if fields:
        fields.append("updated_at = ?")
        params.append(now)
        params.append(post_id)
        query = f"UPDATE posts SET {', '.join(fields)} WHERE id = ?"
        cursor.execute(query, params)
        conn.commit()
    conn.close()

def get_posts(status: Optional[str] = None, db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    if status:
        cursor.execute("SELECT * FROM posts WHERE status = ? ORDER BY created_at DESC", (status,))
    else:
        cursor.execute("SELECT * FROM posts ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_post_by_id(post_id: int, db_path: str = DEFAULT_DB_PATH) -> Optional[Dict[str, Any]]:
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def save_analytics(analytics_data: Dict[str, Any], db_path: str = DEFAULT_DB_PATH) -> int:
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    cursor.execute("""
        INSERT INTO analytics (post_id, linkedin_post_id, views, likes, comments, shares, follower_delta, dm_leads, scraped_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        analytics_data.get("post_id"),
        analytics_data.get("linkedin_post_id", ""),
        analytics_data.get("views", 0),
        analytics_data.get("likes", 0),
        analytics_data.get("comments", 0),
        analytics_data.get("shares", 0),
        analytics_data.get("follower_delta", 0),
        analytics_data.get("dm_leads", 0),
        now
    ))
    analytics_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return analytics_id

def get_all_analytics(db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.*, p.topic, p.angle, p.virality_score, p.predicted_views, p.full_text
        FROM analytics a
        LEFT JOIN posts p ON a.post_id = p.id
        ORDER BY a.scraped_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_auto_comment(target_post_id: str, target_author: str, target_url: str, hashtag: str, comment_text: str, db_path: str = DEFAULT_DB_PATH) -> int:
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    cursor.execute("""
        INSERT INTO auto_comments (target_post_id, target_author, target_url, hashtag, comment_text, posted_at, status)
        VALUES (?, ?, ?, ?, ?, ?, 'posted')
    """, (target_post_id, target_author, target_url, hashtag, comment_text, now))
    comment_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return comment_id

def get_today_auto_comments_count(db_path: str = DEFAULT_DB_PATH) -> int:
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    cursor.execute("SELECT COUNT(*) as cnt FROM auto_comments WHERE posted_at LIKE ?", (f"{today_str}%",))
    row = cursor.fetchone()
    conn.close()
    return row["cnt"] if row else 0

def save_competitor_hooks(hooks: List[Dict[str, Any]], db_path: str = DEFAULT_DB_PATH) -> int:
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    saved = 0
    for h in hooks:
        cursor.execute("""
            INSERT INTO competitor_hooks (influencer_name, original_post, hook_type, hook_text, likes, scraped_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            h.get("influencer_name", ""),
            h.get("original_post", ""),
            h.get("hook_type", "General"),
            h.get("hook_text", ""),
            h.get("likes", 0),
            now
        ))
        saved += 1
    conn.commit()
    conn.close()
    return saved

def get_competitor_hooks(limit: int = 50, db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM competitor_hooks ORDER BY likes DESC, scraped_at DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def set_setting(key: str, value: str, db_path: str = DEFAULT_DB_PATH):
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, ?, ?)", (key, value, now))
    conn.commit()
    conn.close()

def get_setting(key: str, default: str = "", db_path: str = DEFAULT_DB_PATH) -> str:
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row["value"] if row else default
