# employ_toolkit/modules/brand_canvas.py
import json, uuid
from pathlib import Path
from datetime import date

from sqlmodel import Session
from jinja2 import Environment, FileSystemLoader
from employ_toolkit.core.models import CandidateProfile

# ---------- Rutas y plantillas ----------
TEMPLATE_DIR = Path(__file__).parent.parent / "templates"
OUTPUT_DIR = Path("workspace")
OUTPUT_DIR.mkdir(exist_ok=True)

# Preguntas para el wizard de consola
QUESTIONS = [
    ("propósito", "¿Cuál es tu propósito profesional?"),
    ("objetivos", "Menciona 1-2 objetivos a 12 meses."),
    ("audiencia", "¿A qué audiencia quieres llegar?"),
    ("propuesta_valor", "¿Qué te diferencia?"),
    ("logros", "Escribe 2 logros cuantificables."),
    ("pasiones", "¿Qué temas te apasionan?"),
    ("tonalidad", "¿Qué tono quieres proyectar (ej. cercano, formal)?"),
]

# --------------------------------------------------------------------------- #
# 1) Wizard CLI (sigue funcionando para terminal)                             #
# --------------------------------------------------------------------------- #
def brand_canvas_wizard(context: dict):
    """Interfaz CLI simple; sigue preguntando en consola."""
    print("\n=== Wizard · BrandCanvas ===")
    answers = {}
    for key, question in QUESTIONS:
        answers[key] = input(f"{question}\n> ").strip()

    profile: CandidateProfile = context["intake"]
    return _render_brand_canvas(profile, answers, use_html=True)


# --------------------------------------------------------------------------- #
# 2) API silenciosa para la GUI                                               #
# --------------------------------------------------------------------------- #
def generate_brand_canvas(profile: CandidateProfile, answers: dict):
    """
    Genera BrandCanvas sin entrada por consola.
    Devuelve {'json': Path, 'pdf': Path}
    """
    return _render_brand_canvas(profile, answers, use_html=False)


# --------------------------------------------------------------------------- #
# Implementación común                                                        #
# --------------------------------------------------------------------------- #
def _render_brand_canvas(profile: CandidateProfile, answers: dict, *, use_html=True):
    canvas_id = str(uuid.uuid4())[:8]

    # 1. JSON ---------------------------------------------------------------
    json_path = (
        OUTPUT_DIR / f"{profile.full_name}_{canvas_id}_canvas.json"
    )
    data = {"candidate_id": profile.id, "date": str(date.today()), **answers}
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    # 2. PDF ---------------------------------------------------------------
    pdf_path = (
        OUTPUT_DIR / f"{profile.full_name}_{canvas_id}_canvas.pdf"
    )

    if use_html:
        # Render Jinja + WeasyPrint (CLI versión)
        from weasyprint import HTML

        env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        template = env.get_template("brand_canvas.html")
        html_str = template.render(
            name=profile.full_name, answers=answers, today=date.today()
        )
        HTML(string=html_str).write_pdf(pdf_path)
    else:
        # GUI versión con ReportLab (sin dependencias nativas)
        from reportlab.lib.pagesizes import LETTER
        from reportlab.lib.units import inch
        from reportlab.pdfgen import canvas

        c = canvas.Canvas(str(pdf_path), pagesize=LETTER)
        text = c.beginText(1 * inch, 10 * inch)
        text.setFont("Helvetica-Bold", 14)
        text.textLine(f"BrandCanvas · {profile.full_name}")
        text.setFont("Helvetica", 11)
        text.textLine(f"Fecha: {date.today()}\n")

        for key, val in answers.items():
            text.setFont("Helvetica-Bold", 12)
            text.textLine(key.capitalize())
            text.setFont("Helvetica", 11)
            for line in val.splitlines():
                text.textLine(line)
            text.textLine("")

        c.drawText(text)
        c.showPage()
        c.save()

    print(f"✓ BrandCanvas generado:\n  • {json_path}\n  • {pdf_path}\n")
    return {"json": json_path, "pdf": pdf_path}
