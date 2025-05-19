# employ_toolkit/modules/interview.py
from datetime import date
import uuid
from pathlib import Path

from reportlab.lib.pagesizes import LETTER
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

OUTPUT_DIR = Path("workspace")
OUTPUT_DIR.mkdir(exist_ok=True)

SCORE_MAP = {"Bajo": 1, "Medio": 2, "Alto": 3}

BLOCKS = [
    "Personal & Profesional",
    "Formación académica",
    "Experiencia",
    "Soft skills",
    "Hard skills",
]


def generate_interview_pdf(client, scores: dict[str, str], notes: str) -> Path:
    """Crea informe PDF y devuelve la ruta."""
    file_path = OUTPUT_DIR / f"{client.full_name}_{uuid.uuid4().hex[:6]}_interview.pdf"
    doc = SimpleDocTemplate(str(file_path), pagesize=LETTER)
    story = []
    styles = getSampleStyleSheet()

    # Título
    story.append(Paragraph(f"Informe de Entrevista – {client.full_name}", styles["Title"]))
    story.append(Paragraph(f"Fecha: {date.today()}", styles["Normal"]))
    story.append(Spacer(1, 12))

    # Tabla de puntajes
    data = [["Bloque", "Calificación", "Puntos"]]
    for block in BLOCKS:
        level = scores.get(block, "Bajo")
        points = SCORE_MAP[level]
        data.append([block, level, str(points)])

    tbl = Table(data, colWidths=[180, 120, 60])
    tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B6FA4")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ]
        )
    )
    story.append(tbl)
    story.append(Spacer(1, 18))

    # Observaciones
    story.append(Paragraph("Observaciones", styles["Heading3"]))
    story.append(Paragraph(notes.replace("\n", "<br/>"), styles["Normal"]))

    doc.build(story)
    return file_path
