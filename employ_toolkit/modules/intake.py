"""
Módulo · Intake & Diagnóstico
-----------------------------
Recoge los datos básicos del candidato y los persiste en la base
SQLite. Si el email ya existe, actualiza el registro.
"""

from typing import Callable
from sqlmodel import select
from employ_toolkit.core.models import CandidateProfile
from employ_toolkit.core.storage import get_session

VALID_DISC = ("D", "I", "S", "C")

# --------------------------------------------------------------------------- #
# Helpers                                                                     #
# --------------------------------------------------------------------------- #
def _prompt(
    label: str,
    validator: Callable[[str], bool] | None = None,
    error: str = "Dato obligatorio",
) -> str:
    """Entrada con validación básica en CLI."""
    validator = validator or (lambda v: v.strip() != "")
    while True:
        value = input(f"{label}: ").strip()
        if validator(value):
            return value
        print(f"  ⚠ {error}")

# --------------------------------------------------------------------------- #
# Wizard                                                                      #
# --------------------------------------------------------------------------- #
def intake_wizard(context: dict) -> CandidateProfile:
    """Interfaz CLI que crea o actualiza un CandidateProfile y lo devuelve."""
    print("\n=== Wizard · Intake & Diagnóstico ===")
    full_name = _prompt("Nombre completo")
    email = _prompt("Email")
    location = _prompt("Ubicación (ciudad, país)")
    disc = _prompt(
        f"Tipo DISC {VALID_DISC}",
        validator=lambda v: v.upper() in VALID_DISC,
        error="Debe ser D, I, S o C",
    ).upper()

    profile = CandidateProfile(
        full_name=full_name,
        email=email,
        location=location,
        disc_type=disc,
    )

    # ----------------- Persistencia --------------------------------------- #
    with get_session() as session:
        already = session.exec(
            select(CandidateProfile).where(CandidateProfile.email == email)
        ).first()

        if already:
            print("  ⚠ Email ya existe: actualizando registro.")
            profile.id = already.id
            # merge devuelve la instancia vinculada a la sesión
            stored = session.merge(profile)
        else:
            session.add(profile)
            stored = profile

        session.commit()
        session.refresh(stored)

    print(f"✓ Registro guardado con id={stored.id}\n")
    return stored  # Devolvemos la instancia persistente
