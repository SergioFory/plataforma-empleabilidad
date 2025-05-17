from employ_toolkit.modules.intake import intake_wizard
from employ_toolkit.core.storage import init_db

def test_intake_wizard_runs(monkeypatch):
    """El wizard debe crear un perfil sin lanzar excepciones."""
    init_db()

    # Simular respuestas del usuario
    inputs = iter(["Ana Demo", "ana@demo.com", "Bogotá", "I"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    profile = intake_wizard({})
    assert profile.email == "ana@demo.com"
    assert profile.disc_type == "I"
