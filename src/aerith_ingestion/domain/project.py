"""
Project domain model.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Project:
    """A Todoist project."""

    id: str
    name: str
    is_favorite: bool = False
    is_inbox_project: bool = False
    is_team_inbox: bool = False
    is_shared: bool = False
    url: str = ""
    color: str = ""
    parent_id: Optional[str] = None
    order: int = 0
    comment_count: int = 0
    created_at: datetime = None
