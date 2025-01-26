"""
Task repository for SQLite persistence.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from aerith_ingestion.domain.task import Task
from aerith_ingestion.persistence.database import Database


class SQLiteTaskRepository:
    """Repository for persisting tasks in SQLite."""

    def __init__(self, database: Database):
        """Initialize the task repository."""
        self.database = database

    def save(self, task: Task) -> None:
        """Save a task to the database."""
        with Session(self.database.engine) as session:
            session.merge(task)
            session.commit()

    def save_all(self, tasks: List[Task]) -> None:
        """Save multiple tasks to the database."""
        with Session(self.database.engine) as session:
            for task in tasks:
                session.merge(task)
            session.commit()

    def get_by_id(self, task_id: str) -> Optional[Task]:
        """Get a task by its ID."""
        with Session(self.database.engine) as session:
            return session.get(Task, task_id)

    def get_all(self) -> List[Task]:
        """Get all tasks."""
        with Session(self.database.engine) as session:
            return session.query(Task).all()

    def get_by_project_id(self, project_id: str) -> List[Task]:
        """Get all tasks for a project."""
        with Session(self.database.engine) as session:
            return session.query(Task).filter(Task.project_id == project_id).all()

    def delete(self, task_id: str) -> None:
        """Delete a task by its ID."""
        with Session(self.database.engine) as session:
            task = session.get(Task, task_id)
            if task:
                session.delete(task)
                session.commit()

    def delete_all(self) -> None:
        """Delete all tasks."""
        with Session(self.database.engine) as session:
            session.query(Task).delete()
            session.commit()
