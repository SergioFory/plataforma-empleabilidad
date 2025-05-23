from PySide6.QtWidgets import (
    QWidget, QFormLayout, QTextEdit, QTabWidget, QVBoxLayout, QLabel
)


class GenericATSWidget(QWidget):
    """
    Plantilla genérica con las secciones solicitadas para portales
    (Información personal, Experiencia, Educación, etc.).
    Cada sección es un QTextEdit; el widget expone un dict mediante
    los métodos to_dict() / from_dict().
    """
    SECTIONS = [
        ("personal",     "🧑‍💼 Información Personal"),
        ("summary",      "💼 Perfil Profesional / Resumen"),
        ("experience",   "👨‍🔧 Experiencia Laboral"),
        ("education",    "🎓 Formación Académica"),
        ("training",     "📜 Formación Complementaria"),
        ("skills",       "🧰 Habilidades / Competencias"),
        ("languages",    "🗣️ Idiomas"),
        ("references",   "📎 Referencias"),
        ("availability", "⏳ Disponibilidad"),
    ]

    def __init__(self):
        super().__init__()
        vbox = QVBoxLayout(self)

        self.edits = {}
        for key, label in self.SECTIONS:
            vbox.addWidget(QLabel(label))
            te = QTextEdit(); te.setFixedHeight(90)
            vbox.addWidget(te)
            self.edits[key] = te

        vbox.addStretch()

    # ---------- helpers ----------
    def to_dict(self) -> dict:
        return {k: e.toPlainText().strip() for k, e in self.edits.items()}

    def from_dict(self, data: dict):
        for k, e in self.edits.items():
            e.setPlainText(data.get(k, ""))
