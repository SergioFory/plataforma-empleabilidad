# employ_toolkit/modules/comm_style.py
from pathlib import Path
from datetime import date
import uuid

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
)

OUTPUT_DIR = Path("workspace")
OUTPUT_DIR.mkdir(exist_ok=True)          # ← solo una vez el argumento

DISC_DESCRIPTIONS = {
    "D": "Directo, orientado a resultados y muy conciso. Prefiere mensajes breves, cifras claras y un llamado a la acción.",
    "I": "Entusiasta, conversacional y persuasivo. Valora historias, ejemplos y reconocimiento personal.",
    "S": "Cordial, colaborativo y paciente. Le gusta el contexto, la empatía y un ritmo pausado.",
    "C": "Analítico, preciso y estructurado. Exige datos, lógica y documentación de soporte.",
}

def generate_comm_style_pdf(client, category: str, notes: list[str]) -> Path:
    """Genera el PDF de guía de comunicación DISC."""
    file = OUTPUT_DIR / f"{client.full_name}_{uuid.uuid4().hex[:6]}_comm_style.pdf"

    doc    = SimpleDocTemplate(str(file), pagesize=LETTER)
    styles = getSampleStyleSheet()
    story  = [
        Paragraph(f"Guía de Comunicación DISC – {client.full_name}", styles["Title"]),
        Paragraph(f"Fecha: {date.today()}", styles["Normal"]),
        Spacer(1, 12),
        Paragraph(f"Categoría seleccionada: <b>{category}</b>", styles["Heading2"]),
        Paragraph(DISC_DESCRIPTIONS[category], styles["BodyText"]),
        Spacer(1, 12),
    ]

    if notes:
        story.append(Paragraph("Observaciones del consultor:", styles["Heading2"]))
        story.append(
            ListFlowable(
                [ListItem(Paragraph(n, styles["BodyText"])) for n in notes],
                bulletType="bullet"
            )
        )

    doc.build(story)
    return file
