from types import SimpleNamespace
from employ_toolkit.modules import kpi_panel

def test_kpi_xlsx(tmp_path):
    client = SimpleNamespace(full_name="User", id=1)
    cur = {"SSI":50}; meta = {"SSI":80}
    xlsx = kpi_panel.generate_kpi_xlsx(client, cur, meta)
    assert xlsx.exists() and xlsx.suffix == ".xlsx"
    xlsx.unlink()
