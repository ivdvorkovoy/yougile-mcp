from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class Project(BaseModel):
    id: str
    name: str
    archived: bool = False
    raw: dict[str, Any] = Field(default_factory=dict)


class Task(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    project_id: Optional[str] = None
    status: Optional[str] = None
    assignee_id: Optional[str] = None
    due_date: Optional[str] = None
    raw: dict[str, Any] = Field(default_factory=dict)

