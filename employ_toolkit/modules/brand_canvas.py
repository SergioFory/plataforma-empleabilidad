import json, uuid
from pathlib import Path
from datetime import date
from employ_toolkit.core.models import CandidateProfile
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

TEMPLATE_DIR = Path(__file__).parent.parent / "templates"
OUTPUT_DIR = Path("workspace")
OUTPUT_DIR.mkdir(exist_ok=True)

QUESTIONS = [
    ("propósito", "¿Cuál es tu propósito profesional?"),
    ("objetivos", "Menciona 1-2 objetivos a 12 meses."),
    ("audiencia", "¿A qué audiencia quieres llegar?"),
    ("propuesta_valor", "¿Qué te diferencia?"),
    ("logros", "Escribe 2 logros cuantificables."),
    ("pasiones", "¿Qué temas te apasionan?"),
    ("tonalidad", "¿Qué tono quieres proyectar (ej. cercano, formal)?"),
]

def brand_canvas_wizard(context):
    """Interfaz CLI simple para crear el BrandCanvas; genera JSON + PDF."""
    print("\n=== Wizard · BrandCanvas ===")
    answers = {}
    for key, question in QUESTIONS:
        answers[key] = input(f"{question}\n> ").strip()

    profile: CandidateProfile = context["intake"]
    canvas_id = str(uuid.uuid4())[:8]
    filename_json = OUTPUT_DIR / f"{profile.full_name}_{canvas_id}_canvas.json"

    # 1. Guardar JSON
    data = {"candidate_id": profile.id, "date": str(date.today()), **answers}
    filename_json.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    # 2. Renderizar PDF básico
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("brand_canvas.html")
    html_str = template.render(name=profile.full_name, answers=answers, today=date.today())
    pdf_path = OUTPUT_DIR / f"{profile.full_name}_{canvas_id}_canvas.pdf"
    HTML(string=html_str).write_pdf(pdf_path)

    print(f"✓ BrandCanvas generado:\n  • {filename_json}\n  • {pdf_path}\n")
    return {"json": filename_json, "pdf": pdf_path}
