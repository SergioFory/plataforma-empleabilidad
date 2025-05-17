from employ_toolkit.modules.content_plan import content_plan_wizard
from employ_toolkit.core.models import CandidateProfile
from datetime import date

def test_content_plan_file(monkeypatch, tmp_path):
    context = {"intake": CandidateProfile(full_name="Test")}
    monkeypatch.setattr("builtins.input", lambda _: "1")
    monkeypatch.setattr("employ_toolkit.modules.content_plan.OUTPUT_DIR", tmp_path)

    file_path = content_plan_wizard(context)
    assert file_path.exists()
    assert file_path.suffix == ".docx"
