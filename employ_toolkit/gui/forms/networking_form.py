from datetime import date
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QSpinBox, QTextEdit, QCheckBox,
    QWidget, QHBoxLayout, QPushButton, QMessageBox
)

from employ_toolkit.modules import networking
from employ_toolkit.core.models import Document
from employ_toolkit.core.storage import get_session


class NetworkingForm(QDialog):
    TYPES = ["Reclutadores", "Colíderes", "Mentores", "Pares"]

    def __init__(self, client, parent=None):
        super().__init__(parent)
        self.client = client
        self.setWindowTitle(f"Plan Networking – {client.full_name}")
        self.resize(480, 400)

        lay = QFormLayout(self)

        self.meta = QSpinBox(); self.meta.setRange(1, 100); self.meta.setValue(20)
        lay.addRow("Meta conexiones nuevas", self.meta)

        self.chk_types = [QCheckBox(t) for t in self.TYPES]
        lay.addRow("Tipos de contacto", self._row(self.chk_types))

        self.time = QSpinBox(); self.time.setRange(5, 120); self.time.setValue(30)
        lay.addRow("Tiempo diario disponible (min)", self.time)

        self.msg = QTextEdit(); self.msg.setPlaceholderText("Mensaje base…")
        lay.addRow("Mensaje invitación", self.msg)

        btn = QPushButton("Generar PDF")
        btn.clicked.connect(self._generate)
        lay.addRow(btn)

    def _row(self, widgets):
        w = QWidget(); h = QHBoxLayout(w)
        for x in widgets: h.addWidget(x)
        return w

    def _generate(self):
        tipos = [cb.text() for cb in self.chk_types if cb.isChecked()]
        if not tipos:
            QMessageBox.warning(self, "Faltan datos",
                                "Selecciona al menos un tipo de contacto.")
            return
        data = {
            "meta": self.meta.value(),
            "tipos": tipos,
            "mensaje": self.msg.toPlainText(),
            "tiempo": self.time.value(),
        }
        pdf = networking.generate_networking_pdf(self.client, data)

        with get_session() as s:
            s.add(Document(
                client_id=self.client.id, module=1,
                doc_type="networking_plan", path=str(pdf),
                created_at=date.today()
            ))
            s.commit()

        QMessageBox.information(self, "PDF creado", pdf.name)
        self.accept()
