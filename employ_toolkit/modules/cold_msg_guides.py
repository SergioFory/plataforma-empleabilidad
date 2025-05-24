from pathlib import Path
from datetime import date
import uuid

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

OUTPUT_DIR = Path("workspace"); OUTPUT_DIR.mkdir(exist_ok=True)

def generate_cold_pdf(client, messages: dict) -> Path:
    path = OUTPUT_DIR / f"{client.full_name}_{uuid.uuid4().hex[:6]}_cold_msgs.pdf"
    doc = SimpleDocTemplate(str(path), pagesize=LETTER)
    styles = getSampleStyleSheet()
    story = [Paragraph(f"Mensajes en frío – {client.full_name}", styles["Title"]),
             Paragraph(f"Fecha: {date.today()}", styles["Normal"]),
             Spacer(1, 12)]

    for aud, msg in messages.items():
        story += [
            Paragraph(aud, styles["Heading2"]),
            Paragraph(msg.replace("\n", "<br/>"), styles["Normal"]),
            Spacer(1, 12)
        ]
    doc.build(story)
    return path

