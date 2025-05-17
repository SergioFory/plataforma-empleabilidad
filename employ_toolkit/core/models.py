from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class CandidateProfile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str
    email: str
    location: str
    disc_type: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RelevantPosition(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    candidate_id: int = Field(foreign_key="candidateprofile.id")
    title: str
    sector: str
    score: float

