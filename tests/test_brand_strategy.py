from types import SimpleNamespace
from employ_toolkit.modules import personal_brand

def test_strategy_pdf(tmp_path):
    client = SimpleNamespace(full_name="Test", id=1)
    data = {
        "proposito":"Crecer", "objetivos":"OBJ", "audiencia":"IT",
        "pvu":"Soy único", "disc":"D,I"
    }
    p = personal_brand.generate_brand_strategy_pdf(client, data)
    assert p.exists() and p.stat().st_size > 0
    p.unlink()
