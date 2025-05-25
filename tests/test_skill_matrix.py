from types import SimpleNamespace
from employ_toolkit.modules.skills_matrix import generate_skill_matrix_pdf
from pathlib import Path

def test_skill_matrix_pdf(tmp_path):
    client = SimpleNamespace(full_name="Tester", id=1)
    soft = [("Comunicación", "Expresar ideas"), ("Liderazgo", "Influir positivamente")]
    hard = ["Python", "Power BI"]
    pdf = generate_skill_matrix_pdf(client, soft, hard)
    assert Path(pdf).exists() and pdf.suffix == ".pdf"
