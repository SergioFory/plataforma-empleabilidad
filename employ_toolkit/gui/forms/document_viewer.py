# employ_toolkit/gui/forms/document_viewer.py
from pathlib import Path
from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QListWidget, QListWidgetItem,
    QMessageBox, QPushButton, QHBoxLayout
)
from PySide6.QtGui import QDesktopServices

from sqlmodel import select, delete
from employ_toolkit.core.storage import get_session
from employ_toolkit.core.models import Document


class DocumentListDialog(QDialog):
    """Lista (y ahora permite eliminar) los documentos de un cliente."""

    # ------------------------------------------------------------------ #
    def __init__(self, client, parent=None):
        super().__init__(parent)
        self.client = client
        self.setWindowTitle(f"Documentos – {client.full_name}")
        self.resize(520, 420)

        main = QVBoxLayout(self)

        # Lista
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self._open_document)
        self.list_widget.currentRowChanged.connect(
            lambda _: self.btn_delete.setEnabled(self.list_widget.currentItem() is not None)
        )
        main.addWidget(self.list_widget, 1)

        # Botones inferiores
        btn_box = QHBoxLayout()
        self.btn_delete = QPushButton("🗑️ Eliminar")
        self.btn_delete.setEnabled(False)
        self.btn_delete.clicked.connect(self._delete_selected)

        btn_close = QPushButton("Cerrar")
        btn_close.clicked.connect(self.accept)

        btn_box.addWidget(self.btn_delete)
        btn_box.addStretch()
        btn_box.addWidget(btn_close)
        main.addLayout(btn_box)

        # Cargar docs
        self._load_documents()

    # ------------------------------------------------------------------ #
    # Cargar / refrescar lista                                           #
    # ------------------------------------------------------------------ #
    def _load_documents(self):
        """Llena la QListWidget con los documentos del cliente."""
        self.list_widget.clear()
        with get_session() as s:
            docs = s.exec(
                select(Document).where(Document.client_id == self.client.id)
                .order_by(Document.created_at.desc())
            ).all()

        if not docs:
            self.list_widget.addItem("Sin documentos aún.")
            self.list_widget.setEnabled(False)
            self.btn_delete.setEnabled(False)
            return

        self.list_widget.setEnabled(True)
        for doc in docs:
            item = QListWidgetItem(
                f"[{doc.created_at:%Y-%m-%d}]  {doc.doc_type}  →  {Path(doc.path).name}"
            )
            # Guardamos tanto la ruta como el id de DB
            item.setData(Qt.UserRole, (doc.id, Path(doc.path)))
            self.list_widget.addItem(item)

    # ------------------------------------------------------------------ #
    # Abrir con doble-click                                              #
    # ------------------------------------------------------------------ #
    def _open_document(self, item: QListWidgetItem):
        _, file_path = item.data(Qt.UserRole)
        if not file_path.exists():
            QMessageBox.warning(self, "No encontrado",
                                f"El archivo {file_path} no existe.")
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(file_path)))

    # ------------------------------------------------------------------ #
    # Eliminar seleccionado                                              #
    # ------------------------------------------------------------------ #
    def _delete_selected(self):
        item = self.list_widget.currentItem()
        if not item:
            return

        doc_id, file_path = item.data(Qt.UserRole)

        reply = QMessageBox.question(
            self, "Confirmar eliminación",
            f"¿Eliminar el archivo\n{file_path.name}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        # 1) Borrar archivo físico
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception as exc:
                QMessageBox.warning(self, "Error",
                                     f"No se pudo borrar el archivo:\n{exc}")

        # 2) Borrar registro DB
        with get_session() as s:
            s.exec(delete(Document).where(Document.id == doc_id))
            s.commit()

        # 3) Refrescar lista
        self._load_documents()
