from typing import Optional
from sqlmodel import SQLModel, Field, Column, JSON
from datetime import datetime


class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None


class Essay(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Rubric(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    content: str  # Store original rubric text
    criteria: dict = Field(default={}, sa_column=Column(JSON))  # Parsed criteria
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Grading(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    essay_id: int = Field(foreign_key="essay.id")
    rubric_id: int = Field(foreign_key="rubric.id")
    results: dict = Field(default={}, sa_column=Column(JSON))  # Scores, feedback, highlights
    total_score: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
