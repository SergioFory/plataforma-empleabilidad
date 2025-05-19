# employ_toolkit/gui/forms/sector_form.py
from datetime import date
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QTextEdit,
    QPushButton, QMessageBox
)

from employ_toolkit.modules import sector_market
from employ_toolkit.core.models import Document
from employ_toolkit.core.storage import get_session


class SectorForm(QDialog):
    """Captura la información de Sector & Mercado y genera PPTX."""

    def __init__(self, client, parent=None):
        super().__init__(parent)
        self.client = client
        self.setWindowTitle(f"Sector & Mercado – {client.full_name}")
        self.resize(600, 700)

        lay = QFormLayout(self)

        # --- Campos ---
        self.sector     = QLineEdit()
        self.region     = QLineEdit()
        self.empresas   = QTextEdit(); self.empresas.setPlaceholderText("Una por línea")
        self.roles      = QTextEdit(); self.roles.setPlaceholderText("Una por línea")
        self.salarios   = QTextEdit(); self.salarios.setPlaceholderText("Ej: Junior 25-30k")
        self.hards      = QTextEdit()
        self.softs      = QTextEdit()
        self.tendencias = QTextEdit()
        self.retos      = QTextEdit()

        lay.addRow("Sector económico*",          self.sector)
        lay.addRow("Región / País meta*",        self.region)
        lay.addRow("Principales empresas",       self.empresas)
        lay.addRow("Roles más demandados",       self.roles)
        lay.addRow("Rangos salariales",          self.salarios)
        lay.addRow("Habilidades técnicas top",   self.hards)
        lay.addRow("Soft skills top",            self.softs)
        lay.addRow("Tendencias / cifras",        self.tendencias)
        lay.addRow("Retos / pain-points",        self.retos)

        btn = QPushButton("Generar PPTX")
        btn.clicked.connect(self._generate)
        lay.addRow(btn)

    # ------------------------------------------------------------------ #
    def _generate(self):
        if not self.sector.text() or not self.region.text():
            QMessageBox.warning(self, "Faltan datos",
                                "Sector y Región son obligatorios.")
            return

        answers = {
            "sector":     self.sector.text(),
            "region":     self.region.text(),
            "empresas":   self.empresas.toPlainText(),
            "roles":      self.roles.toPlainText(),
            "salarios":   self.salarios.toPlainText(),
            "hards":      self.hards.toPlainText(),
            "softs":      self.softs.toPlainText(),
            "tendencias": self.tendencias.toPlainText(),
            "retos":      self.retos.toPlainText(),
        }

        ppt_path = sector_market.generate_sector_ppt(self.client, answers)

        # Registrar en BD
        with get_session() as s:
            s.add(Document(
                client_id=self.client.id,
                module=1, doc_type="sector_market",
                path=str(ppt_path), created_at=date.today()
            ))
            s.commit()

        QMessageBox.information(self, "Éxito",
                                f"Presentación creada:\n{Path(ppt_path).name}")
        self.accept()
