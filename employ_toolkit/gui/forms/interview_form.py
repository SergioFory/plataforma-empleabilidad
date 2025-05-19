# employ_toolkit/gui/forms/interview_form.py
from datetime import date
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QComboBox, QTextEdit, QPushButton, QMessageBox
)

from employ_toolkit.modules import interview
from employ_toolkit.core.models import Document
from employ_toolkit.core.storage import get_session


LEVELS = ["Bajo", "Medio", "Alto"]


class InterviewForm(QDialog):
    """Formulario de calificación de entrevista estándar."""

    def __init__(self, client, parent=None):
        super().__init__(parent)
        self.client = client
        self.setWindowTitle(f"Entrevista – {client.full_name}")
        self.resize(400, 450)

        lay = QFormLayout(self)

        # Combos para cada bloque
        self.cmb = {}
        for block in interview.BLOCKS:
            cb = QComboBox(); cb.addItems(LEVELS)
            self.cmb[block] = cb
            lay.addRow(block, cb)

        self.notes = QTextEdit()
        lay.addRow("Observaciones", self.notes)

        btn = QPushButton("Generar PDF")
        btn.clicked.connect(self._generate)
        lay.addRow(btn)

    # -------------------------------------------------------------
    def _generate(self):
        scores = {block: combo.currentText() for block, combo in self.cmb.items()}
        notes = self.notes.toPlainText().strip()

        pdf_path = interview.generate_interview_pdf(self.client, scores, notes)

        # Registrar
        with get_session() as s:
            s.add(Document(
                client_id=self.client.id,
                module=1, doc_type="interview_report",
                path=str(pdf_path), created_at=date.today()
            ))
            s.commit()

        QMessageBox.information(self, "Informe creado",
                                f"PDF generado: {pdf_path.name}")
        self.accept()
