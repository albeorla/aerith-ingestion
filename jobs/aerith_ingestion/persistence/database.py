"""
Database setup and connection management.
"""

import sqlite3
from typing import Any, List, Optional, Tuple


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
                    content_hash TEXT
                )
            """
            )

    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection.

        Returns:
            SQLite connection object
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def execute(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> None:
        """Execute a SQL query.

        Args:
            query: SQL query to execute
            params: Optional query parameters
        """
        with self.get_connection() as conn:
            if params:
                conn.execute(query, params)
            else:
                conn.execute(query)
            conn.commit()

    def fetch_one(
        self, query: str, params: Optional[Tuple[Any, ...]] = None
    ) -> Optional[Tuple[Any, ...]]:
        """Execute a query and fetch one result.

        Args:
            query: SQL query to execute
            params: Optional query parameters

        Returns:
            Single result row or None if no results
        """
        with self.get_connection() as conn:
            if params:
                cursor = conn.execute(query, params)
            else:
                cursor = conn.execute(query)
            row = cursor.fetchone()
            return tuple(row) if row else None

    def fetch_all(
        self, query: str, params: Optional[Tuple[Any, ...]] = None
    ) -> List[Tuple[Any, ...]]:
        """Execute a query and fetch all results.

        Args:
            query: SQL query to execute
            params: Optional query parameters

        Returns:
            List of result rows
        """
        with self.get_connection() as conn:
            if params:
                cursor = conn.execute(query, params)
            else:
                cursor = conn.execute(query)
            rows = cursor.fetchall()
            return [tuple(row) for row in rows]

    def truncate_table(self, table_name: str) -> None:
        """Truncate a table, removing all rows while preserving the table structure.

        Args:
            table_name: Name of the table to truncate
        """
        self.execute(f"DELETE FROM {table_name}")
        self.execute("VACUUM")  # Reclaim disk space
