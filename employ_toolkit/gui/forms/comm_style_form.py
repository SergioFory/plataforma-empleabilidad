from datetime import date
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QListWidget,
    QPushButton, QInputDialog, QMessageBox
)

from employ_toolkit.modules.comm_style import generate_comm_style_pdf, DISC_DESCRIPTIONS
from employ_toolkit.core.storage import get_session
from employ_toolkit.core.models import Document


class CommStyleForm(QDialog):
    """Guía de estilo de comunicación según DISC del interlocutor."""

    def __init__(self, client, parent=None):
        super().__init__(parent)
        self.client = client
        self.setWindowTitle(f"Estilo Comunicación DISC – {client.full_name}")
        self.resize(500, 480)

        self.notes: list[str] = []

        # ---- Widgets ----------------------------------------------------
        lbl_cat = QLabel("Elige la categoría DISC del interlocutor:")
        self.cmb_cat = QComboBox()
        self.cmb_cat.addItems(["D", "I", "S", "C"])
        self.cmb_cat.currentTextChanged.connect(self._refresh_description)

        self.lbl_desc = QLabel()
        self.lbl_desc.setWordWrap(True)
        self.lbl_desc.setAlignment(Qt.AlignTop)
        self._refresh_description(self.cmb_cat.currentText())

        self.list_notes = QListWidget()

        btn_add = QPushButton("➕ Añadir nota")
        btn_del = QPushButton("🗑️ Eliminar nota")
        btn_pdf = QPushButton("Exportar PDF")

        btn_add.clicked.connect(self._add_note)
        btn_del.clicked.connect(self._del_note)
        btn_pdf.clicked.connect(self._export_pdf)

        # ---- Layout -----------------------------------------------------
        top = QVBoxLayout()
        top.addWidget(lbl_cat)
        top.addWidget(self.cmb_cat)
        top.addWidget(self.lbl_desc, 1)

        mid = QVBoxLayout()
        mid.addWidget(QLabel("Observaciones del consultor:"))
        mid.addWidget(self.list_notes, 1)

        row_btns = QHBoxLayout()
        row_btns.addWidget(btn_add)
        row_btns.addWidget(btn_del)
        row_btns.addStretch()
        row_btns.addWidget(btn_pdf)

        main = QVBoxLayout(self)
        main.addLayout(top)
        main.addLayout(mid, 1)
        main.addLayout(row_btns)

    # ------------------------------------------------------------------
    def _refresh_description(self, cat: str):
        self.lbl_desc.setText(DISC_DESCRIPTIONS[cat])

    def _add_note(self):
        txt, ok = QInputDialog.getMultiLineText(
            self, "Nueva nota", "Escribe tu observación:"
        )
        if ok and txt.strip():
            self.notes.append(txt.strip())
            self.list_notes.addItem(txt.strip())

    def _del_note(self):
        row = self.list_notes.currentRow()
        if row >= 0:
            self.notes.pop(row)
            self.list_notes.takeItem(row)

    # ------------------------------------------------------------------
    def _export_pdf(self):
        category = self.cmb_cat.currentText()
        pdf_path = generate_comm_style_pdf(self.client, category, self.notes)

        with get_session() as s:
            s.add(Document(
                client_id=self.client.id, module=3,
                doc_type="comm_style", path=str(pdf_path),
                created_at=date.today()
            ))
            s.commit()

        QMessageBox.information(self, "PDF creado",
                                f"Guía exportada: {pdf_path.name}")
        self.accept()
