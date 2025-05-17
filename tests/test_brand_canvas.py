from pathlib import Path
from employ_toolkit.modules.brand_canvas import brand_canvas_wizard
from employ_toolkit.core.models import CandidateProfile
from employ_toolkit.core.storage import init_db

def test_brand_canvas_creates_files(monkeypatch, tmp_path):
    init_db()

    # Mock context con CandidateProfile ficticio
    profile = CandidateProfile(id=1, full_name="Test User", email="t@t.com",
                               location="X", disc_type="D")
    context = {"intake": profile}

    # Respuestas simuladas
    inputs = iter(["A"]*7)
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    # Parchamos OUTPUT_DIR para no ensuciar workspace real
    monkeypatch.setattr("employ_toolkit.modules.brand_canvas.OUTPUT_DIR", tmp_path)

    result = brand_canvas_wizard(context)
    assert result["json"].exists()
    assert result["pdf"].exists()
