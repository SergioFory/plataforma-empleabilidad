from datetime import date
from pathlib import Path
import uuid

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib import colors

OUTPUT_DIR = Path("workspace")
OUTPUT_DIR.mkdir(exist_ok=True)

styles = getSampleStyleSheet()
h1 = styles["Heading1"]
h2 = styles["Heading2"]
normal = styles["BodyText"]

def generate_selection_pdf(client, data: dict) -> Path:
    """
    data = {phase: {"tips":[...], "notes": "..."}}
    """
    path = OUTPUT_DIR / f"{client.full_name}_{uuid.uuid4().hex[:6]}_selection.pdf"
    doc = SimpleDocTemplate(str(path), pagesize=LETTER, title="Ruta Selección")

    story = [
        Paragraph(f"Ruta de Proceso de Selección – {client.full_name}", h1),
        Paragraph(str(date.today()), normal), Spacer(1, 12),
    ]

    for i, (phase, d) in enumerate(data.items(), start=1):
        if i > 1: story.append(PageBreak())
        story.append(Paragraph(f"{i}. {phase}", h2))
        story.append(Spacer(1, 6))

        # tips
        tips_tbl = [[f"• {tip}"] for tip in d["tips"]]
        if tips_tbl:
            tbl = Table(tips_tbl, colWidths=[500])
            tbl.setStyle(TableStyle([
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
            ]))
            story.append(tbl)
            story.append(Spacer(1, 8))

        # notas
        if d["notes"]:
            story.append(Paragraph("<b>Notas / observaciones:</b>", normal))
            story.append(Paragraph(d["notes"].replace("\n", "<br/>"), normal))
            story.append(Spacer(1, 12))

    doc.build(story)
    return path
