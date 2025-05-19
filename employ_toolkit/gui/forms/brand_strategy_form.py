from datetime import date
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QTextEdit, QPushButton, QMessageBox, QCheckBox
)
from employ_toolkit.modules import personal_brand
from employ_toolkit.core.models import Document
from employ_toolkit.core.storage import get_session


class BrandStrategyForm(QDialog):
    def __init__(self, client, parent=None):
        super().__init__(parent)
        self.client = client
        self.setWindowTitle(f"Estrategia de Marca – {client.full_name}")
        self.resize(500, 600)

        lay = QFormLayout(self)

        self.proposito = QLineEdit()
        self.objetivos = QTextEdit();  self.objetivos.setPlaceholderText("Uno por línea (máx 3)")
        self.audiencia = QLineEdit()
        self.pvu       = QLineEdit(maxLength=90)
        self.disc_d = QCheckBox("Dominancia")
        self.disc_i = QCheckBox("Influencia")
        self.disc_s = QCheckBox("Estabilidad")
        self.disc_c = QCheckBox("Conciencia")

        lay.addRow("Propósito", self.proposito)
        lay.addRow("Objetivos 6-12 m", self.objetivos)
        lay.addRow("Audiencia objetivo", self.audiencia)
        lay.addRow("Propuesta de valor (≤ 90 car.)", self.pvu)
        lay.addRow("Diferenciadores DISC",
                   self._disc_row())

        btn = QPushButton("Generar PDF")
        btn.clicked.connect(self._generate)
        lay.addRow(btn)

    def _disc_row(self):
        from PySide6.QtWidgets import QWidget, QHBoxLayout
        w = QWidget(); h = QHBoxLayout(w)
        for cb in (self.disc_d, self.disc_i, self.disc_s, self.disc_c):
            h.addWidget(cb)
        return w

    # --------------------------------------------------
    def _generate(self):
        data = {
            "proposito": self.proposito.text(),
            "objetivos": self.objetivos.toPlainText(),
            "audiencia": self.audiencia.text(),
            "pvu":       self.pvu.text(),
            "disc": ", ".join([cb.text() for cb in
                               (self.disc_d, self.disc_i, self.disc_s, self.disc_c)
                               if cb.isChecked()]) or "N/A",
        }
        pdf_path = personal_brand.generate_brand_strategy_pdf(self.client, data)

        with get_session() as s:
            s.add(Document(
                client_id=self.client.id, module=1,
                doc_type="brand_strategy", path=str(pdf_path),
                created_at=date.today()
            ))
            s.commit()

        QMessageBox.information(self, "PDF creado", pdf_path.name)
        self.accept()
