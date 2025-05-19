from types import SimpleNamespace
from employ_toolkit.modules import interview
from pathlib import Path

def test_interview_pdf(tmp_path):
    client = SimpleNamespace(full_name="Test User", id=1)
    scores = {b: "Alto" for b in interview.BLOCKS}
    notes = "Buen desempeño."
    path = interview.generate_interview_pdf(client, scores, notes)
    assert path.exists() and path.stat().st_size > 0
    path.unlink()
