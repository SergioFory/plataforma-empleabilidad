from employ_toolkit.core.models import CandidateProfile
from employ_toolkit.core.storage import get_session
from sqlmodel import select

VALID_DISC = ("D", "I", "S", "C")

def _prompt(label: str, validator=lambda x: x.strip() != "", error="Dato obligatorio"):
    while True:
        value = input(f"{label}: ").strip()
        if validator(value):
            return value
        print(f"  ⚠ {error}")

def intake_wizard(context):
    """Recoge datos básicos y guarda CandidateProfile; devuelve el objeto."""
    print("\n=== Wizard · Intake & Diagnóstico ===")
    full_name = _prompt("Nombre completo")
    email = _prompt("Email")
    location = _prompt("Ubicación (ciudad, país)")
    disc = _prompt(
        f"Tipo DISC {VALID_DISC}: ",
        validator=lambda v: v.upper() in VALID_DISC,
        error="Debe ser D, I, S o C",
    ).upper()

    profile = CandidateProfile(
        full_name=full_name, email=email, location=location, disc_type=disc
    )

    with get_session() as session:
        # Evitar duplicados por email
        already = session.exec(
            select(CandidateProfile).where(CandidateProfile.email == email)
        ).first()
        if already:
            print("  ⚠ Email ya existe: actualizando registro.")
            profile.id = already.id
            session.merge(profile)
        else:
            session.add(profile)
        session.commit()
        session.refresh(profile)

    print(f"✓ Registro guardado con id={profile.id}\n")
    return profile
