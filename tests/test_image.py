# tests/test_image.py
from types import SimpleNamespace
from pathlib import Path
from employ_toolkit.modules import image_guidelines


def test_image_pdf(tmp_path):
    client = SimpleNamespace(full_name="Tester", id=1)
    data = {
        "sector": "Formal",
        "colores": "Azul marino, gris",
        "accesorios": "Reloj, pañuelo",
        "foto_res": "1080×1080",
        "foto_plano": "Primer plano",
        "foto_fondo": "Neutro",
        "foto_luz": "Natural",
        "banner_msg": "Mensaje profesional para el banner",
        "tipografia": "Arial",
        "paleta_hex": "#0B6FA4, #F4F4F4",   # ← UNA sola cadena
        "logo": "No",
    }

    pdf = image_guidelines.generate_image_guidelines_pdf(client, data)
    assert Path(pdf).exists() and pdf.suffix == ".pdf"
    assert pdf.stat().st_size > 0
    pdf.unlink()        # limpieza
