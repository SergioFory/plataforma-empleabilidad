# employ_toolkit/gui/forms/cold_message_form.py
"""
Mensajes en frío
----------------
• Público a la izquierda (QListWidget)
• A la derecha:
    – Plantilla sugerida (QTextBrowser, solo lectura)
    – Versión editable (QTextEdit)
• “Guardar mensaje” y “Exportar PDF”
"""

from pathlib import Path
from datetime import date
import uuid
from typing import Dict

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QListWidget, QTextBrowser, QTextEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QSplitter
)

from employ_toolkit.modules.cold_msg_guides import generate_cold_pdf
from employ_toolkit.core.storage import get_session
from employ_toolkit.core.models import Document

AUDIENCES = {
    "Recruiter / Headhunter":
"""Hola <Nombre Reclutador>,

Soy <Tu Nombre>, <profesión> con <X años> de experiencia en <industria>.
He seguido las vacantes que publicas y creo que mi logro
<logro clave> encaja perfecto con los roles que manejas.

¿Podríamos agendar una breve llamada de 15 min para contarte cómo podría
aportar a tus procesos?

Gracias y saludos.
<Nombre> | <Teléfono>""",

    "Coordinador(a) de GH":
"""Hola <Nombre>,

Revisé la cultura de <Empresa> y me entusiasma su enfoque en <valor>.
Como <rol objetivo> con trayectoria en <competencia A> y <competencia B>,
quisiera aplicar a futuras vacantes antes de que se publiquen.

Te comparto mi CV adjunto. Quedo atento(a) para ampliar detalles.

Saludos,
<Nombre>""",

    "Gerente de GH":
"""Estimado(a) <Nombre>,

Te contacto porque lidero proyectos de <impacto> que
han generado <resultado cuantificable>. Estoy explorando compañías
donde pueda replicar este éxito y <Empresa> encaja muy bien.

¿Sería posible conversar 10 min esta semana?

Gracias por tu tiempo.
<Nombre>""",

    "Líder de área / Hiring Manager":
"""Hola <Nombre>,

Vi en LinkedIn que tu equipo está creciendo en <área>.
En mi último puesto implementé <proyecto> que elevó <métrica %>.
Creo que podríamos lograr algo similar juntos.

Adjunto CV. ¿Te parece si lo comentamos?

Un saludo,
<Nombre>"""
}

class ColdMessageForm(QDialog):
    def __init__(self, client, parent=None):
        super().__init__(parent)
        self.client = client
        self.setWindowTitle(f"Mensajes en frío – {client.full_name}")
        self.resize(900, 520)

        self.notes: Dict[str, str] = {}          # {audience: mensaje adaptado}

        self.list = QListWidget()
        self.list.addItems(AUDIENCES.keys())
        self.list.currentTextChanged.connect(self._load_audience)

        self.tpl  = QTextBrowser()
        self.tpl.setOpenExternalLinks(True)
        self.edit = QTextEdit()
        self.edit.setPlaceholderText("Edita el mensaje para este público…")

        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.tpl)
        splitter.addWidget(self.edit)
        splitter.setSizes([260, 220])

        btn_save   = QPushButton("Guardar mensaje")
        btn_export = QPushButton("Exportar PDF")
        btn_save.clicked.connect(self._save_current)
        btn_export.clicked.connect(self._export_pdf)

        right = QVBoxLayout()
        right.addWidget(splitter, 1)
        right.addWidget(btn_save)
        right.addWidget(btn_export)

        lay = QHBoxLayout(self)
        lay.addWidget(self.list, 1)
        lay.addLayout(right, 2)

        self.list.setCurrentRow(0)

    # -------- carga / guarda --------
    def _load_audience(self, name: str):
        self.tpl.setPlainText(AUDIENCES[name])
        self.edit.setPlainText(self.notes.get(name, ""))

    def _save_current(self):
        aud = self.list.currentItem().text()
        self.notes[aud] = self.edit.toPlainText().strip()
        QMessageBox.information(self, "Guardado", f"Mensaje para «{aud}» almacenado.")

    # -------- exporta --------
    def _export_pdf(self):
        if not self.notes:
            QMessageBox.warning(self, "Sin mensajes",
                                 "Añade al menos un mensaje personalizado.")
            return
        pdf = generate_cold_pdf(self.client, self.notes)
        with get_session() as s:
            s.add(Document(
                client_id=self.client.id, module=2,
                doc_type="cold_msg_pdf", path=str(pdf),
                created_at=date.today()))
            s.commit()
        QMessageBox.information(self, "PDF creado", f"Guía exportada: {pdf.name}")
        self.accept()
