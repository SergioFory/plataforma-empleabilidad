# employ_toolkit/core/models.py
from typing import Optional
from datetime import datetime, date

from sqlmodel import SQLModel, Field


# --------------------------------------------------------------------------- #
# Módulo 1 – Diagnóstico & Marca                                              #
# --------------------------------------------------------------------------- #
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


# --------------------------------------------------------------------------- #
# Users & Clientes                                                            #
# --------------------------------------------------------------------------- #
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password_hash: str
    role: str = Field(default="consultor")  # admin | consultor


class Client(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str
    email: str
    phone: str
    profession: str
    age: int
    disc_type: str


# --------------------------------------------------------------------------- #
# Documentos generados                                                        #
# --------------------------------------------------------------------------- #
class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    client_id: int = Field(foreign_key="client.id")
    module: int               # 1, 2 o 3
    doc_type: str             # brand_canvas, content_plan, etc.
    path: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


# --------------------------------------------------------------------------- #
# NUEVA TABLA – CVData  (Módulo 2)                                            #
# --------------------------------------------------------------------------- #
class CVData(SQLModel, table=True):
    """
    Guarda el CV optimizado y la versión estructurada en JSON
    para poder re-editarlo más adelante.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    client_id: int = Field(foreign_key="client.id")
    updated_at: date
    json_blob: str            # CV estructurado (texto JSON)
    pdf_path: str             # archivo PDF generado
    docx_path: str            # archivo DOCX generado
