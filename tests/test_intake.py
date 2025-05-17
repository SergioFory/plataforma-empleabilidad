from employ_toolkit.core.storage import init_db, get_session
from employ_toolkit.core.models import CandidateProfile
from employ_toolkit.modules.intake import intake_wizard

def test_intake_wizard_saves(monkeypatch):
    init_db()

    # Simula entradas de usuario
    inputs = iter(["Ana Pérez", "ana@test.com", "Bogotá, CO", "I"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    profile = intake_wizard({})

    with get_session() as session:
        stored = session.get(CandidateProfile, profile.id)

    assert stored is not None
    assert stored.email == "ana@test.com"
    assert stored.disc_type == "I"
