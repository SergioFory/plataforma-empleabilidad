from pathlib import Path
from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QListWidget, QListWidgetItem, QMessageBox
)
from PySide6.QtGui import QDesktopServices

from sqlmodel import select
from employ_toolkit.core.storage import get_session
from employ_toolkit.core.models import Document


class DocumentListDialog(QDialog):
    """Lista los documentos generados para un cliente."""

    def __init__(self, client, parent=None):
        super().__init__(parent)
        self.client = client
        self.setWindowTitle(f"Documentos – {client.full_name}")
        self.resize(450, 400)

        layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        self._load_documents()
        self.list_widget.itemDoubleClicked.connect(self._open_document)

    # ------------------------------------------------------------------ #
    def _load_documents(self):
        with get_session() as s:
            docs = s.exec(
                select(Document).where(Document.client_id == self.client.id)
                .order_by(Document.created_at.desc())
            ).all()

        if not docs:
            self.list_widget.addItem("Sin documentos aún.")
            self.list_widget.setEnabled(False)
            return

        for doc in docs:
            item = QListWidgetItem(
                f"[{doc.created_at}] {doc.doc_type}  →  {Path(doc.path).name}"
            )
            item.setData(Qt.UserRole, Path(doc.path))
            self.list_widget.addItem(item)

    def _open_document(self, item: QListWidgetItem):
        file_path: Path = item.data(Qt.UserRole)
        if not file_path.exists():
            QMessageBox.warning(self, "No encontrado",
                                f"El archivo {file_path} no existe.")
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(file_path)))
