import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class Topic(BaseModel):
    id: str
    title: str
    summary: str
    category: str
    impact_score: float
    difficulty_estimate: str
    sources: List[str]
    discovered_at: str
    status: str = "pending_selection"  # pending_selection/selected/in_progress/completed


class TopicDatabase:
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Get project root and create data directory
            project_root = Path(__file__).parent.parent.parent.parent
            db_path = project_root / "data" / "topics.db"

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize the database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS topics (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    category TEXT NOT NULL,
                    impact_score REAL NOT NULL,
                    difficulty_estimate TEXT NOT NULL,
                    sources TEXT NOT NULL,  -- JSON array
                    discovered_at TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending_selection'
                )
            """)
            conn.commit()

    def save_topic(self, topic: Topic) -> bool:
        """Save a topic to the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO topics
                    (id, title, summary, category, impact_score, difficulty_estimate, sources, discovered_at, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    topic.id,
                    topic.title,
                    topic.summary,
                    topic.category,
                    topic.impact_score,
                    topic.difficulty_estimate,
                    json.dumps(topic.sources),
                    topic.discovered_at,
                    topic.status
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error saving topic: {e}")
            return False

    def get_pending_topics(self, limit: int = 15) -> List[Topic]:
        """Get topics waiting for selection."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM topics WHERE status = 'pending_selection' ORDER BY impact_score DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()

            topics = []
            for row in rows:
                topic_data = dict(row)
                topic_data['sources'] = json.loads(topic_data['sources'])
                topics.append(Topic(**topic_data))
            return topics

    def get_topic_by_id(self, topic_id: str) -> Optional[Topic]:
        """Get a specific topic by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM topics WHERE id = ?", (topic_id,))
            row = cursor.fetchone()

            if row:
                topic_data = dict(row)
                topic_data['sources'] = json.loads(topic_data['sources'])
                return Topic(**topic_data)
            return None

    def update_topic_status(self, topic_id: str, status: str) -> bool:
        """Update the status of a topic."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "UPDATE topics SET status = ? WHERE id = ?",
                    (status, topic_id)
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating topic status: {e}")
            return False

    def get_all_topics(self) -> List[Topic]:
        """Get all topics from the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM topics ORDER BY discovered_at DESC")
            rows = cursor.fetchall()

            topics = []
            for row in rows:
                topic_data = dict(row)
                topic_data['sources'] = json.loads(topic_data['sources'])
                topics.append(Topic(**topic_data))
            return topics

    def get_topics_by_category(self, category: str) -> List[Topic]:
        """Get topics filtered by category."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM topics WHERE category = ? ORDER BY impact_score DESC",
                (category,)
            )
            rows = cursor.fetchall()

            topics = []
            for row in rows:
                topic_data = dict(row)
                topic_data['sources'] = json.loads(topic_data['sources'])
                topics.append(Topic(**topic_data))
            return topics