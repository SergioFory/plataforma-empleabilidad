"""
Ruta de Proceso de Selección (Módulo 3-D)
-----------------------------------------
• Stepper con 5 fases estándar.
• Cada fase contiene una lista editable de tips + notas libres.
• Exporta un PDF con la información visible y registra el documento.
"""

from datetime import date
from pathlib import Path
from typing import Dict, List

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QTabWidget, QListWidget, QListWidgetItem, QTextEdit,
    QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QInputDialog,
    QMessageBox
)

from employ_toolkit.modules.selection_route import generate_selection_pdf
from employ_toolkit.core.storage import get_session
from employ_toolkit.core.models import Document


PHASES = [
    "Análisis de Vacante",
    "Screening Telefónico",
    "Entrevista HR",
    "Entrevista Técnica / Panel",
    "Oferta & Cierre",
]

# tips base, feel free to editar en runtime
DEFAULT_TIPS: Dict[str, List[str]] = {
    "Análisis de Vacante": [
        "Estudiar descripción y valores de la compañía",
        "Identificar 3–5 keywords técnicas",
        "Preparar ejemplos STAR alineados a requisitos"
    ],
    "Screening Telefónico": [
        "Rapport inicial de 30 seg",
        "Pitch profesional (60 seg)",
        "Preguntar siguiente paso y tiempos"
    ],
    "Entrevista HR": [
        "Conectar logros con cultura organizacional",
        "Usar ejemplos STAR para competencias blandas",
        "Preparar preguntas inteligentes sobre el rol"
    ],
    "Entrevista Técnica / Panel": [
        "Responder con estructura CAR",
        "Pensar en voz alta en retos algorítmicos",
        "Mostrar curiosidad y buenas prácticas"
    ],
    "Oferta & Cierre": [
        "Analizar paquete completo (salario + beneficios)",
        "Comunicar motivadores clave al negociarlos",
        "Agradecer y confirmar fecha de inicio"
    ],
}

OUTPUT_DIR = Path("workspace")
OUTPUT_DIR.mkdir(exist_ok=True)


class PhaseWidget(QWidget):
    """Widget interno para cada pestaña."""
    def __init__(self, phase: str, tips: List[str]):
        super().__init__()
        self.phase = phase
        self.tips_list = QListWidget()
        for t in tips:
            self.tips_list.addItem(QListWidgetItem(t))

        # botones CRUD
        btn_add = QPushButton("➕")
        btn_edit = QPushButton("✏️")
        btn_del = QPushButton("🗑️")
        btn_add.clicked.connect(self._add_tip)
        btn_edit.clicked.connect(self._edit_tip)
        btn_del.clicked.connect(self._del_tip)

        btn_row = QHBoxLayout()
        for b in (btn_add, btn_edit, btn_del): btn_row.addWidget(b)
        btn_row.addStretch()

        # notas libres
        self.notes = QTextEdit()
        self.notes.setPlaceholderText("Notas / observaciones del role-play …")

        lay = QVBoxLayout(self)
        lay.addLayout(btn_row)
        lay.addWidget(self.tips_list)
        lay.addWidget(self.notes)

    # CRUD handlers
    def _add_tip(self):
        text, ok = QInputDialog.getMultiLineText(self, "Nuevo Tip", "Tip detallado:")
        if ok and text.strip():
            self.tips_list.addItem(QListWidgetItem(text.strip()))

    def _edit_tip(self):
        item = self.tips_list.currentItem()
        if not item: return
        text, ok = QInputDialog.getMultiLineText(self, "Editar Tip", "Tip detallado:", item.text())
        if ok and text.strip():
            item.setText(text.strip())

    def _del_tip(self):
        row = self.tips_list.currentRow()
        if row >= 0:
            self.tips_list.takeItem(row)

    # extracción para PDF
    def export_data(self):
        return {
            "tips": [self.tips_list.item(i).text() for i in range(self.tips_list.count())],
            "notes": self.notes.toPlainText().strip()
        }


class SelectionRouteForm(QDialog):
    """Diálogo principal."""
    def __init__(self, client, parent=None):
        super().__init__(parent)
        self.client = client
        self.setWindowTitle(f"Ruta de Selección – {client.full_name}")
        self.resize(900, 560)

        self.tabs = QTabWidget()
        self.phase_widgets: Dict[str, PhaseWidget] = {}
        for ph in PHASES:
            pw = PhaseWidget(ph, DEFAULT_TIPS.get(ph, []))
            self.phase_widgets[ph] = pw
            self.tabs.addTab(pw, ph)

        btn_pdf = QPushButton("Exportar PDF")
        btn_pdf.clicked.connect(self._export_pdf)

        lay = QVBoxLayout(self)
        lay.addWidget(self.tabs, 1)
        lay.addWidget(btn_pdf, alignment=Qt.AlignRight)

    # ---------------------------------------------------- #
    def _export_pdf(self):
        data = {ph: w.export_data() for ph, w in self.phase_widgets.items()}
        pdf_path = generate_selection_pdf(self.client, data)

        # registrar
        with get_session() as s:
            s.add(Document(
                client_id=self.client.id, module=3,
                doc_type="selection_route", path=str(pdf_path),
                created_at=date.today()
            ))
            s.commit()

        QMessageBox.information(self, "PDF creado",
                                f"Ruta exportada: {pdf_path.name}")
        self.accept()
