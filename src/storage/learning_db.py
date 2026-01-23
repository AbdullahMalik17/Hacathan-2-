"""
Learning Database - Store and retrieve user preferences and patterns.
Local-first with encryption support.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import hashlib


class LearningDatabase:
    """
    Local SQLite database for storing learned preferences and patterns.

    Features:
    - User preferences with confidence scores
    - Approval patterns for learning
    - Contact intelligence
    - Task history for similarity matching
    """

    def __init__(self, db_path: str = "Vault/Data/learning.db"):
        """
        Initialize learning database.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self._initialize_db()

    def _initialize_db(self):
        """Create database schema if it doesn't exist."""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries

        cursor = self.conn.cursor()

        # User preferences table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                confidence REAL DEFAULT 0.5,
                source TEXT DEFAULT 'observed',
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(category, key)
            )
        """)

        # Approval patterns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS approval_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_type TEXT NOT NULL,
                context TEXT,
                approved INTEGER NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Contact intelligence table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contact_intelligence (
                email TEXT PRIMARY KEY,
                name TEXT,
                relationship TEXT,
                importance_score REAL DEFAULT 0.5,
                last_interaction TIMESTAMP,
                communication_frequency INTEGER DEFAULT 0,
                topics TEXT,
                notes TEXT
            )
        """)

        # Task history table (for similarity matching)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_history (
                id TEXT PRIMARY KEY,
                intent TEXT NOT NULL,
                domain TEXT NOT NULL,
                complexity_score REAL,
                risk_score REAL,
                approach TEXT,
                success INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()

    # --- User Preferences ---

    def store_preference(
        self,
        category: str,
        key: str,
        value: Any,
        confidence: float = 0.7,
        source: str = "observed"
    ):
        """
        Store or update a user preference.

        Args:
            category: Preference category (e.g., 'writing_style', 'music_taste')
            key: Preference key (e.g., 'greeting_style', 'work_genre')
            value: Preference value (will be JSON-encoded)
            confidence: Confidence in this preference (0-1)
            source: How this was learned ('explicit', 'observed', 'inferred')
        """
        cursor = self.conn.cursor()

        value_json = json.dumps(value)

        cursor.execute("""
            INSERT INTO user_preferences (category, key, value, confidence, source, last_updated)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(category, key) DO UPDATE SET
                value = excluded.value,
                confidence = excluded.confidence,
                source = excluded.source,
                last_updated = CURRENT_TIMESTAMP
        """, (category, key, value_json, confidence, source))

        self.conn.commit()

    def get_preference(
        self,
        category: str,
        key: str,
        default: Any = None
    ) -> Optional[Any]:
        """
        Get a user preference.

        Args:
            category: Preference category
            key: Preference key
            default: Default value if not found

        Returns:
            Preference value or default
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT value FROM user_preferences
            WHERE category = ? AND key = ?
        """, (category, key))

        row = cursor.fetchone()
        if row:
            return json.loads(row['value'])
        return default

    def get_all_preferences(self, category: str = None) -> List[Dict]:
        """
        Get all preferences, optionally filtered by category.

        Args:
            category: Optional category filter

        Returns:
            List of preference dictionaries
        """
        cursor = self.conn.cursor()

        if category:
            cursor.execute("""
                SELECT * FROM user_preferences WHERE category = ?
                ORDER BY confidence DESC
            """, (category,))
        else:
            cursor.execute("""
                SELECT * FROM user_preferences
                ORDER BY category, confidence DESC
            """)

        return [dict(row) for row in cursor.fetchall()]

    # --- Approval Patterns ---

    def record_approval(
        self,
        action_type: str,
        approved: bool,
        context: Dict = None
    ):
        """
        Record user approval or rejection.

        Args:
            action_type: Type of action (e.g., 'email_send', 'social_post')
            approved: Whether user approved
            context: Additional context (JSON-encoded)
        """
        cursor = self.conn.cursor()

        context_json = json.dumps(context or {})

        cursor.execute("""
            INSERT INTO approval_patterns (action_type, context, approved, timestamp)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """, (action_type, context_json, 1 if approved else 0))

        self.conn.commit()

    def get_approval_rate(
        self,
        action_type: str,
        context_filter: Dict = None,
        days: int = 30
    ) -> float:
        """
        Get approval rate for an action type.

        Args:
            action_type: Type of action
            context_filter: Optional context filter
            days: Look back this many days

        Returns:
            Approval rate (0-1)
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT AVG(approved) as approval_rate
            FROM approval_patterns
            WHERE action_type = ?
                AND timestamp >= datetime('now', '-' || ? || ' days')
        """, (action_type, days))

        row = cursor.fetchone()
        return row['approval_rate'] if row and row['approval_rate'] is not None else 0.5

    # --- Contact Intelligence ---

    def update_contact(
        self,
        email: str,
        name: str = None,
        relationship: str = None,
        importance_score: float = None,
        topics: List[str] = None,
        notes: str = None
    ):
        """
        Update contact intelligence.

        Args:
            email: Contact email
            name: Contact name
            relationship: Relationship type ('client', 'vendor', 'colleague', 'personal')
            importance_score: Importance score (0-1)
            topics: List of topics discussed
            notes: Additional notes
        """
        cursor = self.conn.cursor()

        # Build update query dynamically
        updates = []
        params = []

        if name:
            updates.append("name = ?")
            params.append(name)

        if relationship:
            updates.append("relationship = ?")
            params.append(relationship)

        if importance_score is not None:
            updates.append("importance_score = ?")
            params.append(importance_score)

        if topics:
            updates.append("topics = ?")
            params.append(json.dumps(topics))

        if notes:
            updates.append("notes = ?")
            params.append(notes)

        updates.append("last_interaction = CURRENT_TIMESTAMP")
        updates.append("communication_frequency = communication_frequency + 1")

        params.append(email)

        cursor.execute(f"""
            INSERT INTO contact_intelligence (email, name, relationship, importance_score, topics, notes, last_interaction, communication_frequency)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, 1)
            ON CONFLICT(email) DO UPDATE SET
                {', '.join(updates)}
        """, [email, name, relationship, importance_score or 0.5, json.dumps(topics or []), notes] + params)

        self.conn.commit()

    def get_contact(self, email: str) -> Optional[Dict]:
        """
        Get contact intelligence.

        Args:
            email: Contact email

        Returns:
            Contact dictionary or None
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT * FROM contact_intelligence WHERE email = ?
        """, (email,))

        row = cursor.fetchone()
        if row:
            contact = dict(row)
            if contact.get('topics'):
                contact['topics'] = json.loads(contact['topics'])
            return contact
        return None

    # --- Task History ---

    def store_task(
        self,
        task_id: str,
        intent: str,
        domain: str,
        complexity_score: float,
        risk_score: float,
        approach: str,
        success: bool
    ):
        """
        Store task execution for future similarity matching.

        Args:
            task_id: Unique task ID
            intent: Task intent
            domain: Task domain
            complexity_score: Complexity score
            risk_score: Risk score
            approach: Approach taken
            success: Whether task succeeded
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT INTO task_history (id, intent, domain, complexity_score, risk_score, approach, success, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(id) DO UPDATE SET
                success = excluded.success,
                timestamp = CURRENT_TIMESTAMP
        """, (task_id, intent, domain, complexity_score, risk_score, approach, 1 if success else 0))

        self.conn.commit()

    async def find_similar(
        self,
        intent: str,
        domain: str,
        limit: int = 5
    ) -> List[str]:
        """
        Find similar past tasks.

        Uses simple text similarity for now, can be enhanced with embeddings.

        Args:
            intent: Task intent
            domain: Task domain
            limit: Maximum number of similar tasks

        Returns:
            List of task IDs
        """
        cursor = self.conn.cursor()

        # Simple similarity: same domain + intent keyword match
        # In production, use embeddings or fuzzy matching
        intent_words = set(intent.lower().split())

        cursor.execute("""
            SELECT id, intent FROM task_history
            WHERE domain = ?
            ORDER BY timestamp DESC
            LIMIT 50
        """, (domain,))

        tasks = []
        for row in cursor.fetchall():
            task_intent_words = set(row['intent'].lower().split())
            similarity = len(intent_words & task_intent_words) / max(len(intent_words), len(task_intent_words), 1)

            if similarity > 0.3:  # Threshold
                tasks.append((row['id'], similarity))

        # Sort by similarity and return top N
        tasks.sort(key=lambda x: x[1], reverse=True)
        return [task_id for task_id, _ in tasks[:limit]]

    def get_task_stats(self, days: int = 30) -> Dict:
        """
        Get task execution statistics.

        Args:
            days: Look back this many days

        Returns:
            Statistics dictionary
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT
                COUNT(*) as total_tasks,
                SUM(success) as successful_tasks,
                AVG(complexity_score) as avg_complexity,
                AVG(risk_score) as avg_risk
            FROM task_history
            WHERE timestamp >= datetime('now', '-' || ? || ' days')
        """, (days,))

        row = cursor.fetchone()
        if row:
            stats = dict(row)
            if stats['total_tasks'] > 0:
                stats['success_rate'] = stats['successful_tasks'] / stats['total_tasks']
            else:
                stats['success_rate'] = 0.0
            return stats

        return {
            'total_tasks': 0,
            'successful_tasks': 0,
            'avg_complexity': 0.0,
            'avg_risk': 0.0,
            'success_rate': 0.0
        }

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
