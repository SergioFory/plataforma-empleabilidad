from datetime import date, timedelta
from docx import Document
from pathlib import Path

OUTPUT_DIR = Path("workspace")
OUTPUT_DIR.mkdir(exist_ok=True)

PILLARS = ["Conocimiento", "Experiencias", "Opinión"]
FORMATS = ["Artículo", "Post", "Video"]

def content_plan_wizard(context):
    """Genera un plan de contenido semanal durante 1 mes."""
    print("\n=== Plan de Contenidos ===")
    frecuencia = int(input("¿Publicaciones por semana (ej. 2)? ").strip() or "2")

    # Generar fechas
    today = date.today()
    calendar = []
    for week in range(4):
        for i in range(frecuencia):
            d = today + timedelta(days=week*7 + i)
            pillar = PILLARS[(week + i) % len(PILLARS)]
            fmt = FORMATS[(week + i) % len(FORMATS)]
            calendar.append((d, pillar, fmt))

    # Crear DOCX
    doc = Document()
    doc.add_heading("Plan de Contenido · LinkedIn", 0)
    table = doc.add_table(rows=1, cols=3)
    hdr = table.rows[0].cells
    hdr[0].text, hdr[1].text, hdr[2].text = "Fecha", "Pilar", "Formato"
    for d, pillar, fmt in calendar:
        row = table.add_row().cells
        row[0].text, row[1].text, row[2].text = str(d), pillar, fmt

    file_path = OUTPUT_DIR / f"content_plan_{today}.docx"
    doc.save(file_path)
    print(f"✓ Plan de Contenidos generado en {file_path}")
    return file_path
