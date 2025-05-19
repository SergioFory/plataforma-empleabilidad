from datetime import date
import uuid
from pathlib import Path

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

OUTPUT_DIR = Path("workspace")
OUTPUT_DIR.mkdir(exist_ok=True)


def generate_brand_strategy_pdf(client, data: dict) -> Path:
    """
    Crea PDF con propósito, objetivos, audiencia, PVU y diferenciadores DISC.
    """
    file_path = OUTPUT_DIR / f"{client.full_name}_{uuid.uuid4().hex[:6]}_strategy.pdf"
    doc = SimpleDocTemplate(str(file_path), pagesize=LETTER)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(f"Estrategia de Marca Personal – {client.full_name}",
                           styles["Title"]))
    story.append(Paragraph(f"Fecha: {date.today()}", styles["Normal"]))
    story.append(Spacer(1, 12))

    # Tabla principal
    table_data = [
        ["Propósito", data["proposito"]],
        ["Objetivos (6-12 m)", "<br/>".join(data["objetivos"].splitlines())],
        ["Audiencia", data["audiencia"]],
        ["Propuesta de valor", data["pvu"]],
        ["Diferenciadores DISC", data["disc"]],
    ]
    tbl = Table(table_data, colWidths=[160, 350])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B6FA4")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 18))

    story.append(Paragraph(
        "Timeline sugerido: Fase 1 (Mes 1-2) visibilidad – Fase 2 (Mes 3-4) autoridad – "
        "Fase 3 (Mes 5-6) posicionamiento avanzado.", styles["Italic"]))

    doc.build(story)
    return file_path
