from employ_toolkit.modules import sector_market
from types import SimpleNamespace
import os

def test_sector_ppt(tmp_path):
    client = SimpleNamespace(full_name="Test User", id=1)
    answers = {"sector":"IT","region":"LATAM","empresas":"A\nB",
               "roles":"Dev\nQA","salarios":"Junior 20k","hards":"",
               "softs":"","tendencias":"","retos":""}
    path = sector_market.generate_sector_ppt(client, answers)
    assert path.exists()
    assert path.suffix == ".pptx"
    os.remove(path)
