from pathlib import Path
from datetime import date
import uuid
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    ListFlowable, ListItem
)

OUTPUT_DIR = Path("workspace")
OUTPUT_DIR.mkdir(exist_ok=True)


def _bullets_from_dict(d: dict, styles) -> ListFlowable:
    items = []
    for k, v in d.items():
        if v:
            label = k.capitalize().replace('_', ' ')
            text  = v.replace('\n', '<br/>')
            items.append(ListItem(Paragraph(f"<b>{label}:</b> {text}", styles["Normal"]),
                                  leftIndent=10, bulletFontName="Helvetica"))
    return ListFlowable(items, bulletType="bullet")


def generate_ats_pdf(client, data: dict) -> Path:
    path = OUTPUT_DIR / f"{client.full_name}_{uuid.uuid4().hex[:6]}_ats.pdf"
    doc = SimpleDocTemplate(str(path), pagesize=LETTER)
    st  = getSampleStyleSheet()
    story = [
        Paragraph(f"Guía de Perfiles – {client.full_name}", st["Title"]),
        Paragraph(f"Fecha: {date.today()}", st["Normal"]),
        Spacer(1, 12),
    ]
    h2 = st["Heading2"]
    normal = st["Normal"]

    for site, content in data.items():
        story.append(Paragraph(site, h2))
        if isinstance(content, dict):
            story.append(_bullets_from_dict(content, st))
        else:  # nunca ocurrirá ya, pero se deja por seguridad
            story.append(Paragraph(str(content).replace('\n', '<br/>'), normal))
        story.append(Spacer(1, 12))

    doc.build(story)
    return path
