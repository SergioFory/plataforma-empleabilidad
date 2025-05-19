# employ_toolkit/gui/main.py
"""
Ventana Principal
-----------------
• Tabla de clientes, botón “Nuevo”.
• Doble-clic → BrandCanvas.
• 📂 Documentos – visor.
• 📊 Sector & Mercado – PPTX.
• 🔗 Perfil LinkedIn – PDF.
• 📝 Entrevista – PDF.
• 📑 Estrategia Marca – PDF.
• 📅 Parrilla Contenido – DOCX + XLSX.
• 🤝 Networking – PDF.
• 📈 KPIs – XLSX.
• 🖼️ Imagen Prof. – PDF.
"""

from typing import List

from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableView, QTabWidget, QMessageBox,
)

from sqlmodel import select

from employ_toolkit.core.storage import get_session
from employ_toolkit.core.models import Client

# Formularios GUI
from employ_toolkit.gui.forms.intake_form import IntakeForm
from employ_toolkit.gui.forms.brand_canvas_form import BrandCanvasForm
from employ_toolkit.gui.forms.document_viewer import DocumentListDialog
from employ_toolkit.gui.forms.sector_form import SectorForm
from employ_toolkit.gui.forms.link_form import LinkedInForm
from employ_toolkit.gui.forms.interview_form import InterviewForm
from employ_toolkit.gui.forms.brand_strategy_form import BrandStrategyForm
from employ_toolkit.gui.forms.content_plan_form import ContentPlanForm
from employ_toolkit.gui.forms.networking_form import NetworkingForm
from employ_toolkit.gui.forms.kpi_form import KPIForm
from employ_toolkit.gui.forms.image_form import ImageForm                     # ← nuevo

# --------------------------------------------------------------------------- #
# Modelo QTableView                                                           #
# --------------------------------------------------------------------------- #
class ClientTableModel(QAbstractTableModel):
    HEADERS = ["ID", "Nombre", "Email", "Profesión"]

    def __init__(self, data: List[Client]):
        super().__init__()
        self._data = data

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self.HEADERS)

    def data(self, index, role=Qt.DisplayRole):
        if not (index.isValid() and role == Qt.DisplayRole):
            return None
        c = self._data[index.row()]
        return {0: c.id, 1: c.full_name, 2: c.email, 3: c.profession}[index.column()]

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.HEADERS[section]

    def client_at(self, row: int) -> Client:
        return self._data[row]


# --------------------------------------------------------------------------- #
# MainWindow                                                                  #
# --------------------------------------------------------------------------- #
class MainWindow(QMainWindow):
    def __init__(self, username: str, role: str):
        super().__init__()
        self.setWindowTitle("Plataforma de Empleabilidad")
        self.resize(1050, 670)

        # ---------------- Barra lateral ----------------
        sidebar = QWidget()
        s_lay = QVBoxLayout(sidebar)
        lbl_user = QLabel(f"👤 {username} ({role})", alignment=Qt.AlignCenter)
        lbl_user.setFont(QFont("Arial", 10, QFont.Bold))

        btn_mod1 = QPushButton("Módulo 1 · Diagnóstico & Marca")
        btn_mod1.clicked.connect(lambda: self.tabs.setCurrentIndex(0))
        btn_mod2 = QPushButton("Módulo 2 · Presencia Digital")
        btn_mod3 = QPushButton("Módulo 3 · Skills & Selección")

        # Botones dependientes de selección
        self.btn_linkedin   = QPushButton("🔗 Perfil LinkedIn")
        self.btn_sector     = QPushButton("📊 Sector & Mercado")
        self.btn_strategy   = QPushButton("📑 Estrategia Marca")
        self.btn_calendar   = QPushButton("📅 Parrilla Contenido")
        self.btn_network    = QPushButton("🤝 Networking")
        self.btn_kpis       = QPushButton("📈 KPIs")
        self.btn_image      = QPushButton("🖼️ Imagen Prof.")        # ← nuevo
        self.btn_interview  = QPushButton("📝 Entrevista")
        self.btn_docs       = QPushButton("📂 Documentos del Cliente")

        dep_buttons = (
            self.btn_linkedin, self.btn_sector, self.btn_strategy,
            self.btn_calendar, self.btn_network, self.btn_kpis,
            self.btn_image, self.btn_interview, self.btn_docs
        )
        for b in dep_buttons:
            b.setEnabled(False)

        # Conexiones
        self.btn_linkedin.clicked.connect(self._open_linkedin_form)
        self.btn_sector.clicked.connect(self._open_sector_form)
        self.btn_strategy.clicked.connect(self._open_strategy_form)
        self.btn_calendar.clicked.connect(self._open_calendar_form)
        self.btn_network.clicked.connect(self._open_network_form)
        self.btn_kpis.clicked.connect(self._open_kpi_form)
        self.btn_image.clicked.connect(self._open_image_form)        # ← nuevo
        self.btn_interview.clicked.connect(self._open_interview_form)
        self.btn_docs.clicked.connect(self._open_documents)

        # Orden visual
        for w in (
            lbl_user, btn_mod1, btn_mod2, btn_mod3,
            self.btn_linkedin, self.btn_sector,
            self.btn_strategy, self.btn_calendar,
            self.btn_network, self.btn_kpis,
            self.btn_image,                       # ← nuevo
            self.btn_interview, self.btn_docs
        ):
            s_lay.addWidget(w)
        s_lay.addStretch()

        # ---------------- Pestañas principales ----------
        self.tabs = QTabWidget()
        self._init_tab_clients()

        # ---------------- Layout raíz -------------------
        container = QWidget()
        main_lay = QHBoxLayout(container)
        main_lay.addWidget(sidebar, 1)
        main_lay.addWidget(self.tabs, 4)
        self.setCentralWidget(container)

    # ----------------- TAB CLIENTES ------------------- #
    def _init_tab_clients(self):
        tab = QWidget(); lay = QVBoxLayout(tab)

        btn_new = QPushButton("➕ Nuevo Cliente")
        btn_new.clicked.connect(self._open_intake_form)

        self.table = QTableView()
        self._load_clients()
        self.table.doubleClicked.connect(self._double_click_client)
        self.table.selectionModel().currentRowChanged.connect(self._row_changed)

        lay.addWidget(btn_new)
        lay.addWidget(self.table)
        self.tabs.addTab(tab, "Clientes")

    def _load_clients(self):
        with get_session() as s:
            data = s.exec(select(Client).order_by(Client.id.desc())).all()
        self.model = ClientTableModel(data)
        self.table.setModel(self.model)
        self.table.resizeColumnsToContents()

    # ------------------- Slots ------------------- #
    def _row_changed(self, current, _prev):
        valid = current.isValid()
        for b in (
            self.btn_docs, self.btn_sector, self.btn_linkedin,
            self.btn_strategy, self.btn_calendar,
            self.btn_network, self.btn_kpis,
            self.btn_image, self.btn_interview
        ):
            b.setEnabled(valid)

    def _open_intake_form(self):
        if IntakeForm(self).exec() == IntakeForm.Accepted:
            self._load_clients()

    def _double_click_client(self, idx: QModelIndex):
        client = self.model.client_at(idx.row())
        if BrandCanvasForm(client, self).exec() == BrandCanvasForm.Accepted:
            QMessageBox.information(self, "Documento guardado",
                                    "BrandCanvas registrado para el cliente.")
            self._row_changed(idx, None)

    # ---- Helpers ----
    def _current_client(self):
        idx = self.table.currentIndex()
        return self.model.client_at(idx.row()) if idx.isValid() else None

    # ---- Formularios ----
    def _open_documents(self):
        client = self._current_client()
        if client:
            DocumentListDialog(client, self).exec()

    def _open_sector_form(self):
        client = self._current_client()
        if client:
            SectorForm(client, self).exec()

    def _open_linkedin_form(self):
        client = self._current_client()
        if client:
            LinkedInForm(client, self).exec()

    def _open_interview_form(self):
        client = self._current_client()
        if client:
            InterviewForm(client, self).exec()

    def _open_strategy_form(self):
        client = self._current_client()
        if client:
            BrandStrategyForm(client, self).exec()

    def _open_calendar_form(self):
        client = self._current_client()
        if client:
            ContentPlanForm(client, self).exec()

    def _open_network_form(self):
        client = self._current_client()
        if client:
            NetworkingForm(client, self).exec()

    def _open_kpi_form(self):
        client = self._current_client()
        if client:
            KPIForm(client, self).exec()

    def _open_image_form(self):                       # ← nuevo
        client = self._current_client()
        if client:
            ImageForm(client, self).exec()


# ---------------------------- Debug ---------------------------- #
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    win = MainWindow("demo", "consultor")
    win.show()
    sys.exit(app.exec())
