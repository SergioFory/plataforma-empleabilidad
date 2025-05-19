from types import SimpleNamespace
from employ_toolkit.modules import content_plan

def test_content_plan_file(tmp_path):
    client = SimpleNamespace(full_name="User", id=1)
    params = {"pilares":["Conocimiento"], "freq":1,
              "formatos":["Post"], "semanas":4}
    paths = content_plan.generate_content_plan(client, params)
    assert paths["xlsx"].exists() and paths["xlsx"].suffix == ".xlsx"
    paths["xlsx"].unlink()
    paths["docx"].unlink()
