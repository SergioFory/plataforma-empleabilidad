# employ_toolkit/modules/image_guidelines.py
from datetime import date
from pathlib import Path
import uuid

from reportlab.lib.pagesizes import LETTER
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)

OUTPUT_DIR = Path("workspace")
OUTPUT_DIR.mkdir(exist_ok=True)


def generate_image_guidelines_pdf(client, data: dict) -> Path:
    """
    data keys:
        sector, colores, accesorios,
        foto_res, foto_plano, foto_fondo, foto_luz,
        banner_msg, tipografia, paleta_hex, logo
    """
    path = OUTPUT_DIR / f"{client.full_name}_{uuid.uuid4().hex[:6]}_image.pdf"
    doc = SimpleDocTemplate(str(path), pagesize=LETTER)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(f"Guía de Imagen Profesional – {client.full_name}", styles["Title"]))
    story.append(Paragraph(f"Fecha: {date.today()}", styles["Normal"]))
    story.append(Spacer(1, 12))

    # --- Estilo común para tablas ---
    tbl_style = TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B6FA4")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ])

    # -------- Vestimenta --------
    table1 = Table([
        ["Sector", data["sector"]],
        ["Colores recomendados", data["colores"]],
        ["Accesorios", data["accesorios"]],
    ], colWidths=[200, 320])
    table1.setStyle(tbl_style)

    story.append(Paragraph("Vestimenta", styles["Heading2"]))
    story.append(table1)
    story.append(Spacer(1, 16))

    # -------- Foto --------
    table2 = Table([
        ["Resolución", data["foto_res"]],
        ["Plano", data["foto_plano"]],
        ["Fondo", data["foto_fondo"]],
        ["Iluminación", data["foto_luz"]],
    ], colWidths=[200, 320])
    table2.setStyle(tbl_style)

    story.append(Paragraph("Foto Profesional", styles["Heading2"]))
    story.append(table2)
    story.append(Spacer(1, 16))

    # -------- Banner --------
    story.append(Paragraph("Banner de LinkedIn", styles["Heading2"]))
    story.append(Paragraph(f"Mensaje visual sugerido: {data['banner_msg']}", styles["Normal"]))
    story.append(Spacer(1, 12))

    # -------- Consistencia visual --------
    story.append(Paragraph("Consistencia visual", styles["Heading2"]))
    story.append(Paragraph(
        f"Tipografía: {data['tipografia']} &nbsp;&nbsp; "
        f"Paleta: {data['paleta_hex']} &nbsp;&nbsp; "
        f"¿Logo personal?: {data['logo']}", styles["Normal"]
    ))

    doc.build(story)
    return path
