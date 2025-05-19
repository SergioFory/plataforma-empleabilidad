# tests/test_networking.py
from types import SimpleNamespace
from pathlib import Path

from employ_toolkit.modules import networking


def test_networking_pdf(tmp_path):
    """
    Verifica que generate_networking_pdf cree un PDF válido.
    """
    # Cliente ficticio
    client = SimpleNamespace(full_name="Tester", id=1)

    # Datos mínimos de entrada
    data = {
        "meta": 10,
        "tipos": ["Reclutadores"],
        "mensaje": "¡Hola, me encantaría conectar contigo!",
        "tiempo": 30,
    }

    pdf_path = networking.generate_networking_pdf(client, data)

    assert Path(pdf_path).exists()
    assert pdf_path.suffix == ".pdf"
    assert pdf_path.stat().st_size > 0

    # Limpieza
    pdf_path.unlink()
