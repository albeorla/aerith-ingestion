"""
Project repository for SQLite persistence.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from aerith_ingestion.domain.project import Project
from aerith_ingestion.persistence.database import Database


class SQLiteProjectRepository:
    """Repository for persisting projects in SQLite."""

    def __init__(self, database: Database):
        """Initialize the project repository."""
        self.database = database

    def save(self, project: Project) -> None:
        """Save a project to the database."""
        with Session(self.database.engine) as session:
            session.merge(project)
            session.commit()

    def save_all(self, projects: List[Project]) -> None:
        """Save multiple projects to the database."""
        with Session(self.database.engine) as session:
            for project in projects:
                session.merge(project)
            session.commit()

    def get_by_id(self, project_id: str) -> Optional[Project]:
        """Get a project by its ID."""
        with Session(self.database.engine) as session:
            return session.get(Project, project_id)

    def get_all(self) -> List[Project]:
        """Get all projects."""
        with Session(self.database.engine) as session:
            return session.query(Project).all()

    def delete(self, project_id: str) -> None:
        """Delete a project by its ID."""
        with Session(self.database.engine) as session:
            project = session.get(Project, project_id)
            if project:
                session.delete(project)
                session.commit()

    def delete_all(self) -> None:
        """Delete all projects."""
        with Session(self.database.engine) as session:
            session.query(Project).delete()
            session.commit()
