# employ_toolkit/gui/forms/link_form.py
from datetime import date
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton,
    QFileDialog, QMessageBox
)

from employ_toolkit.core.models import Document
from employ_toolkit.core.storage import get_session


ANALYSIS_URL = "https://reepl.io/free-tools/linkedin-profile-analysis?utm_source=chatgpt.com"


class LinkedInForm(QDialog):
    """Abre la web de análisis y permite adjuntar el PDF resultante."""

    def __init__(self, client, parent=None):
        super().__init__(parent)
        self.client = client
        self.setWindowTitle(f"Análisis LinkedIn – {client.full_name}")
        self.resize(500, 170)

        lay = QVBoxLayout(self)
        lay.addWidget(QLabel(
            "1. Se abrirá la página de análisis de LinkedIn en tu navegador.\n"
            "2. Genera el informe PDF y descárgalo.\n"
            "3. Haz clic en “Adjuntar PDF” para registrarlo."
        ))

        btn_open = QPushButton("Abrir página de análisis")
        btn_open.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(ANALYSIS_URL)))

        btn_attach = QPushButton("Adjuntar PDF")
        btn_attach.clicked.connect(self._attach_pdf)

        lay.addWidget(btn_open)
        lay.addWidget(btn_attach)

    # ------------------------------------------------------------------ #
    def _attach_pdf(self):
        file, _ = QFileDialog.getOpenFileName(
            self, "Selecciona el PDF generado",
            "", "PDF Files (*.pdf)"
        )
        if not file:
            return

        pdf_path = Path(file)
        with get_session() as s:
            s.add(Document(
                client_id=self.client.id,
                module=1, doc_type="linkedin_report",
                path=str(pdf_path), created_at=date.today()
            ))
            s.commit()

        QMessageBox.information(
            self, "¡Informe registrado!", f"Se guardó: {pdf_path.name}"
        )
        self.accept()
