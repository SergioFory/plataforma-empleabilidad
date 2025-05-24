from pathlib import Path
from datetime import date
import uuid

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

OUTPUT_DIR = Path("workspace")
OUTPUT_DIR.mkdir(exist_ok=True)

DESCRIPTIONS = {
    "Alertas de Google":
        "Crea una búsqueda con operadores (AND, OR, \"\") y activa la alerta "
        "para recibir correos diarios/semanales.",
    "Búsqueda avanzada LinkedIn":
        "Emplea filtros de ubicación, empresa, y palabras clave con Boolean "
        "para acotar resultados.",
    "Filtros de portales de empleo":
        "Aprovecha filtros de rango salarial, fecha de publicación y trabajo remoto.",
    "Boolean X-Ray (site:linkedin)":
        "Ejemplo: site:linkedin.com/in AND \"Recruiter\" AND \"company name\".",
    "Hashtags sectoriales":
        "Sigue hashtags relevantes y activa notificaciones.",
    "Grupos & Comunidades":
        "Únete a grupos en LinkedIn, Discord o Slack y participa activamente.",
    "Networking de segundo grado":
        "Identifica conexiones mutuas y solicita presentación personalizada.",
}

def generate_search_pdf(client, data: dict) -> Path:
    path = OUTPUT_DIR / f"{client.full_name}_{uuid.uuid4().hex[:6]}_search.pdf"
    doc = SimpleDocTemplate(str(path), pagesize=LETTER)
    st  = getSampleStyleSheet()
    story = [Paragraph("Guía de Búsqueda Activa de Empleo", st["Title"]),
             Paragraph(f"{client.full_name} – {date.today()}", st["Normal"]),
             Spacer(1, 12)]

    for name, notes in data.items():
        if not notes.strip():
            continue
        story += [
            Paragraph(name, st["Heading2"]),
            Paragraph(DESCRIPTIONS.get(name, ""), st["BodyText"]),
            Spacer(1, 4),
            Paragraph(f"<b>Ejemplo / Parámetros:</b><br/>{notes.replace(chr(10), '<br/>')}",
                      st["BodyText"]),
            Spacer(1, 12),
        ]

    doc.build(story)
    return path
