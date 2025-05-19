# employ_toolkit/gui/forms/brand_canvas_form.py
from datetime import date

from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QTextEdit,
    QPushButton,
    QMessageBox,
)

from employ_toolkit.modules import brand_canvas
from employ_toolkit.core.models import Document
from employ_toolkit.core.storage import get_session


class BrandCanvasForm(QDialog):
    """Diálogo para capturar los datos del BrandCanvas y generar PDF."""

    def __init__(self, client, parent=None):
        super().__init__(parent)
        self.client = client
        self.setWindowTitle(f"BrandCanvas – {client.full_name}")
        self.resize(500, 600)

        layout = QFormLayout(self)

        self.proposito = QTextEdit();  self.proposito.setFixedHeight(40)
        self.objetivos = QTextEdit();  self.objetivos.setFixedHeight(40)
        self.audiencia = QTextEdit();  self.audiencia.setFixedHeight(40)
        self.valor     = QTextEdit();  self.valor.setFixedHeight(40)
        self.difer     = QTextEdit();  self.difer.setFixedHeight(40)
        self.logros    = QTextEdit();  self.logros.setFixedHeight(40)
        self.pasiones  = QTextEdit();  self.pasiones.setFixedHeight(40)
        self.tono      = QTextEdit();  self.tono.setFixedHeight(40)

        layout.addRow("Propósito: ¿Cuál es tu propósito profesional?",               self.proposito)
        layout.addRow("Objetivos (6-12 m): Menciona 1-2 objetivos a 12 meses.",      self.objetivos)
        layout.addRow("Audiencia objetivo: ¿A qué audiencia quieres llegar?",      self.audiencia)
        layout.addRow("Propuesta de valor: ¿Qué te diferencia?",      self.valor)
        layout.addRow("Diferenciadores DISC",    self.difer)
        layout.addRow("Logros cuantificables: Escribe 2 logros cuantificables.",   self.logros)
        layout.addRow("Pasiones / temas: ¿Qué temas te apasionan?",        self.pasiones)
        layout.addRow("Tono: ¿Qué tono quieres proyectar (ej. cercano, formal)?",                    self.tono)

        btn_generate = QPushButton("Generar PDF")
        btn_generate.clicked.connect(self.generate_pdf)
        layout.addRow(btn_generate)

    # ------------------------------------------------------------------ #
    def generate_pdf(self):
        """Recoge respuestas, genera PDF/JSON y registra el documento."""
        answers = {
            "propósito":        self.proposito.toPlainText(),
            "objetivos":        self.objetivos.toPlainText(),
            "audiencia":        self.audiencia.toPlainText(),
            "propuesta_valor":  self.valor.toPlainText(),
            "diferenciadores":  self.difer.toPlainText(),
            "logros":           self.logros.toPlainText(),
            "pasiones":         self.pasiones.toPlainText(),
            "tonalidad":        self.tono.toPlainText(),
        }

        # Genera silenciosamente (sin CLI) y devuelve rutas
        result = brand_canvas.generate_brand_canvas(self.client, answers)

        # Registra documento en la base de datos
        with get_session() as s:
            doc = Document(
                client_id=self.client.id,
                module=1,
                doc_type="brand_canvas",
                path=str(result["pdf"]),
                created_at=date.today(),
            )
            s.add(doc)
            s.commit()

        QMessageBox.information(
            self, "Éxito", "BrandCanvas PDF generado y registrado."
        )
        self.accept()

