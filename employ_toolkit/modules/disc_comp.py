"""
Genera el PDF de competencias DISC seleccionadas
------------------------------------------------
Se llama desde DISCCompForm.  Devuelve la ruta del PDF generado.
"""

from pathlib import Path
from datetime import date
import uuid

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors


OUTPUT_DIR = Path("workspace")
OUTPUT_DIR.mkdir(exist_ok=True)


def _table(cat: str, comps: dict[str, str]):
    """Devuelve una tabla ReportLab con las competencias chequeadas."""
    data = [["Categoría DISC", "Competencia", "Definición"]]
    for name, desc in comps.items():
        data.append([cat, name, desc])

    t = Table(data, colWidths=[85, 150, 280])
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B6FA4")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return t


def generate_disc_comp_pdf(client, cat1: str, comp1: dict[str, str],
                           cat2: str, comp2: dict[str, str]) -> Path:
    styles = getSampleStyleSheet()
    story  = []

    story.append(Paragraph(f"Competencias DISC – {client.full_name}", styles["Title"]))
    story.append(Paragraph(f"Fecha: {date.today()}", styles["Normal"]))
    story.append(Spacer(1, 12))

    if comp1:
        story.append(_table(cat1, comp1))
        story.append(Spacer(1, 24))

    if comp2:
        story.append(_table(cat2, comp2))

    pdf_path = OUTPUT_DIR / f"{client.full_name}_{uuid.uuid4().hex[:6]}_disc.pdf"
    SimpleDocTemplate(str(pdf_path), pagesize=LETTER).build(story)
    return pdf_path
