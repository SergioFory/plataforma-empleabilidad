from pathlib import Path
from datetime import date
import uuid
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

OUTPUT_DIR = Path("workspace")
OUTPUT_DIR.mkdir(exist_ok=True)

def generate_skill_matrix_pdf(client, soft: dict[str, str],
                              hard: list[tuple[str, str]]) -> Path:
    """
    soft: {skill: definición}
    hard: [(skill, plataforma), ...]   # lista ordenada
    """
    path = OUTPUT_DIR / f"{client.full_name}_{uuid.uuid4().hex[:6]}_skills.pdf"
    doc   = SimpleDocTemplate(str(path), pagesize=LETTER)
    styles = getSampleStyleSheet()
    story  = []

    story += [Paragraph(f"Skill Matrix – {client.full_name}", styles["Title"]),
              Paragraph(f"Fecha: {date.today()}", styles["Normal"]),
              Spacer(1, 12)]

    # ------------ Soft skills ------------
    story.append(Paragraph("Soft skills prioritarias", styles["Heading2"]))

    data = [["Skill", "Definición"]] + [[k, v] for k, v in soft.items()]
    tbl  = Table(data, colWidths=[180, 330])
    tbl.setStyle(TableStyle([
        ("GRID",  (0, 0), (-1, -1), 0.4, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#005B8F")),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
    ]))
    story += [tbl, Spacer(1, 18)]

    # ------------ Hard skills ------------
    story.append(Paragraph("Hard skills recomendadas", styles["Heading2"]))
    for s, platform in hard:
        story.append(Paragraph(f"• <b>{s}</b>  <span size=9>(Formarse en {platform})</span>",
                               styles["Normal"]))

    doc.build(story)
    return path
