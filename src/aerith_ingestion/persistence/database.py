"""
Database setup and connection management.
"""

import sqlite3


class Database:
    def __init__(self, db_path: str = "todoist.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database tables."""
        with self.get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    is_shared BOOLEAN NOT NULL DEFAULT 0,
                    is_favorite BOOLEAN NOT NULL DEFAULT 0,
                    is_inbox_project BOOLEAN NOT NULL DEFAULT 0,
                    is_team_inbox BOOLEAN NOT NULL DEFAULT 0,
                    order_index INTEGER NOT NULL DEFAULT 0,
                    parent_id TEXT,
                    last_updated TEXT NOT NULL
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    description TEXT,
                    project_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    priority INTEGER NOT NULL DEFAULT 1,
                    order_index INTEGER NOT NULL DEFAULT 0,
                    is_completed BOOLEAN NOT NULL DEFAULT 0,
                    parent_id TEXT,
                    section_id TEXT,
                    due_date TEXT,
                    due_string TEXT,
                    due_recurring BOOLEAN,
                    vector_id TEXT,
                    embedding_model TEXT,
                    content_hash TEXT,
                    processed_at TEXT,
                    FOREIGN KEY(project_id) REFERENCES projects(id)
                )
            """
            )

    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection with row factory enabled."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
