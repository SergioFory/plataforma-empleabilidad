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

# ---------------------------------------------------------------------------
# NUEVA TABLA: User
# ---------------------------------------------------------------------------
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password_hash: str
    role: str = Field(default="consultor")  # valores: admin | consultor

# ------------------------------------------------------------------- #
# Tabla Client                                                        #
# ------------------------------------------------------------------- #
class Client(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str
    email: str
    phone: str
    profession: str
    age: int
    disc_type: str

# ------------------------------------------------------------------- #
# Tabla Document                                                      #
# ------------------------------------------------------------------- #
from datetime import datetime
class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    client_id: int = Field(foreign_key="client.id")
    module: int               # 1, 2 o 3
    doc_type: str             # brand_canvas, content_plan, etc.
    path: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
