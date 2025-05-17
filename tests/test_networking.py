from employ_toolkit.modules.linkedin_networking import networking_ppt
from employ_toolkit.core.models import CandidateProfile
from pathlib import Path

def test_ppt_created(tmp_path):
    context = {"intake": CandidateProfile(full_name="Tester")}
    file = networking_ppt(context)
    assert Path(file).exists()
    assert file.suffix == ".pptx"
