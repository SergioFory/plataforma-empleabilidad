from datetime import date
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QSpinBox, QPushButton,
    QCheckBox, QHBoxLayout, QWidget, QMessageBox
)

from employ_toolkit.modules import content_plan
from employ_toolkit.core.models import Document
from employ_toolkit.core.storage import get_session


class ContentPlanForm(QDialog):
    """
    Formulario para crear la parrilla de contenidos (DOCX + XLSX calendario).
    """
    PILLARS = ["Conocimiento", "Experiencias", "Opinión"]
    FORMATS = ["Post", "Artículo", "Carousel", "Video", "Podcast corto"]

    def __init__(self, client, parent=None):
        super().__init__(parent)
        self.client = client
        self.setWindowTitle(f"Parrilla Contenidos – {client.full_name}")
        self.resize(450, 400)

        lay = QFormLayout(self)

        # -------- Pilares --------
        self.chk_pillars = [QCheckBox(p) for p in self.PILLARS]
        lay.addRow("Pilares", self._row(self.chk_pillars))

        # -------- Frecuencia semanal --------
        self.freq = QSpinBox()
        self.freq.setRange(1, 7)
        self.freq.setValue(3)
        lay.addRow("Publicaciones / semana", self.freq)

        # -------- Formatos --------
        self.chk_formats = [QCheckBox(f) for f in self.FORMATS]
        lay.addRow("Formatos permitidos", self._row(self.chk_formats))

        # -------- Semanas piloto --------
        self.semanas = QSpinBox()
        self.semanas.setRange(4, 12)
        self.semanas.setValue(8)
        lay.addRow("Duración piloto (semanas)", self.semanas)

        # -------- Botón generar --------
        btn = QPushButton("Generar DOCX & XLSX")
        btn.clicked.connect(self._generate)
        lay.addRow(btn)

    # ------------------------------------------------------------------ #
    def _row(self, widgets):
        w = QWidget()
        h = QHBoxLayout(w)
        for x in widgets:
            h.addWidget(x)
        return w

    # ------------------------------------------------------------------ #
    def _generate(self):
        pillars = [cb.text() for cb in self.chk_pillars if cb.isChecked()]
        formats = [cb.text() for cb in self.chk_formats if cb.isChecked()]

        if not pillars or not formats:
            QMessageBox.warning(
                self,
                "Faltan datos",
                "Selecciona al menos un pilar y un formato."
            )
            return

        params = {
            "pilares": pillars,
            "freq": self.freq.value(),
            "formatos": formats,
            "semanas": self.semanas.value(),
        }

        paths = content_plan.generate_content_plan(self.client, params)   # {'docx':..., 'xlsx':...}

        # Registrar en la base de documentos
        with get_session() as s:
            for kind, path in paths.items():       # kind = 'docx' | 'xlsx'
                s.add(Document(
                    client_id=self.client.id,
                    module=1,
                    doc_type=f"content_plan_{kind}",
                    path=str(path),
                    created_at=date.today()
                ))
            s.commit()

        QMessageBox.information(
            self,
            "Archivos creados",
            f"DOCX: {paths['docx'].name}\nXLSX: {paths['xlsx'].name}"
        )
        self.accept()
