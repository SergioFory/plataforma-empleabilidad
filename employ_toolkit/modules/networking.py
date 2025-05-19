# employ_toolkit/modules/networking.py
from datetime import date
import uuid
from pathlib import Path

from reportlab.lib.pagesizes import LETTER
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

OUTPUT_DIR = Path("workspace")
OUTPUT_DIR.mkdir(exist_ok=True)


def generate_networking_pdf(client, data: dict) -> Path:
    """
    data = {meta:int, tipos:list[str], mensaje:str, tiempo:int}
    """
    file_path = OUTPUT_DIR / f"{client.full_name}_{uuid.uuid4().hex[:6]}_networking.pdf"
    doc = SimpleDocTemplate(str(file_path), pagesize=LETTER)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(f"Plan de Networking – {client.full_name}", styles["Title"]))
    story.append(Paragraph(f"Fecha: {date.today()}", styles["Normal"]))
    story.append(Spacer(1, 12))

    table = Table([
        ["Meta conexiones nuevas", str(data["meta"])],
        ["Tipos de contacto", ", ".join(data["tipos"])],
        ["Tiempo diario disponible (min)", str(data["tiempo"])],
    ], colWidths=[220, 300])
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B6FA4")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ]))
    story.append(table)
    story.append(Spacer(1, 18))

    story.append(Paragraph("Mensaje base de invitación", styles["Heading3"]))
    story.append(Paragraph(data["mensaje"].replace("\n", "<br/>"), styles["Normal"]))

    story.append(Spacer(1, 18))
    story.append(Paragraph(
        "Checklist diario: 1) Buscar contactos, 2) Personalizar mensaje, "
        "3) Registrar seguimiento.", styles["Italic"]))

    doc.build(story)
    return file_path
