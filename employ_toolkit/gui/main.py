# employ_toolkit/gui/main.py
"""
Ventana Principal
-----------------
• Tabla de clientes, botón “Nuevo”.
• Doble-clic → BrandCanvas.
• Botones por módulo (se muestran al pulsar Módulo 1 / 2 / 3).
• 📂 Documentos visible siempre.
"""

from typing import List
from functools import partial

from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableView, QTabWidget, QMessageBox,
)

from sqlmodel import select
from employ_toolkit.core.storage import get_session
from employ_toolkit.core.models import Client

# ---------- Formularios ----------
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
from employ_toolkit.gui.forms.image_form import ImageForm
from employ_toolkit.gui.forms.cv_form import CVForm
from employ_toolkit.gui.forms.ats_form import ATSForm
from employ_toolkit.gui.forms.cold_message_form import ColdMessageForm

# --------------------------------------------------------------- #
# Modelo de Tabla                                                 #
# --------------------------------------------------------------- #
class ClientTableModel(QAbstractTableModel):
    HEADERS = ["ID", "Nombre", "Email", "Profesión"]

    def __init__(self, data: List[Client]):
        super().__init__()
        self._data = data

    def rowCount(self, _p=QModelIndex()):
        return len(self._data)

    def columnCount(self, _p=QModelIndex()):
        return len(self.HEADERS)

    def data(self, ix, role=Qt.DisplayRole):
        if role != Qt.DisplayRole or not ix.isValid():
            return None
        c = self._data[ix.row()]
        return {0: c.id, 1: c.full_name, 2: c.email, 3: c.profession}[ix.column()]

    def headerData(self, s, orient, role=Qt.DisplayRole):
        return self.HEADERS[s] if role == Qt.DisplayRole and orient == Qt.Horizontal else None

    def client_at(self, row: int) -> Client:
        return self._data[row]

# --------------------------------------------------------------- #
# MainWindow                                                      #
# --------------------------------------------------------------- #
class MainWindow(QMainWindow):
    def __init__(self, username: str, role: str):
        super().__init__()
        self.setWindowTitle("Plataforma de Empleabilidad")
        self.resize(1050, 670)

        # --------------- Barra lateral ---------------
        sidebar = QWidget()
        s_lay = QVBoxLayout(sidebar)

        lbl_user = QLabel(f"👤 {username} ({role})", alignment=Qt.AlignCenter)
        lbl_user.setFont(QFont("Arial", 10, QFont.Bold))

        # Selector módulo
        btn_mod1 = QPushButton("Módulo 1 · Diagnóstico & Marca")
        btn_mod2 = QPushButton("Módulo 2 · Presencia Digital")
        btn_mod3 = QPushButton("Módulo 3 · Skills & Selección")
        btn_mod1.clicked.connect(partial(self._switch_module, 1))
        btn_mod2.clicked.connect(partial(self._switch_module, 2))
        btn_mod3.clicked.connect(partial(self._switch_module, 3))

        # ---- Acciones M1
        self.btn_linkedin  = QPushButton("🔗 Perfil LinkedIn")
        self.btn_sector    = QPushButton("📊 Sector & Mercado")
        self.btn_strategy  = QPushButton("📑 Estrategia Marca")
        self.btn_calendar  = QPushButton("📅 Parrilla Contenido")
        self.btn_network   = QPushButton("🤝 Networking")
        self.btn_kpis      = QPushButton("📈 KPIs")
        self.btn_image     = QPushButton("🖼️ Imagen Prof.")
        self.btn_interview = QPushButton("📝 Entrevista")

        # ---- Acciones M2
        self.btn_cv     = QPushButton("📄 CV Optimizado")
        self.btn_ats    = QPushButton("🌐 ATS & Plataformas")
        self.btn_search = QPushButton("🔍 Técnicas Búsqueda")
        self.btn_cold   = QPushButton("✉️ Mensajes en frío")   # ← NUEVO

        # ---- Acciones M3 (placeholder)
        self.mod3_btns: List[QPushButton] = []

        # ---- Documentos
        self.btn_docs = QPushButton("📂 Documentos del Cliente")

        # Agrupar por módulo
        self.mod1_btns = [
            self.btn_linkedin, self.btn_sector, self.btn_strategy,
            self.btn_calendar, self.btn_network, self.btn_kpis,
            self.btn_image, self.btn_interview,
        ]
        self.mod2_btns = [
            self.btn_cv, self.btn_ats, self.btn_search, self.btn_cold  # agregado
        ]

        # Ocultar M2/M3 al inicio
        for b in self.mod2_btns + self.mod3_btns:
            b.hide()

        # -------- Conexiones --------
        self.btn_linkedin.clicked.connect(self._open_linkedin_form)
        self.btn_sector.clicked.connect(self._open_sector_form)
        self.btn_strategy.clicked.connect(self._open_strategy_form)
        self.btn_calendar.clicked.connect(self._open_calendar_form)
        self.btn_network.clicked.connect(self._open_network_form)
        self.btn_kpis.clicked.connect(self._open_kpi_form)
        self.btn_image.clicked.connect(self._open_image_form)
        self.btn_interview.clicked.connect(self._open_interview_form)

        self.btn_cv.clicked.connect(self._open_cv_form)
        self.btn_ats.clicked.connect(self._open_ats_form)
        self.btn_search.clicked.connect(self._open_search_form)
        self.btn_cold.clicked.connect(self._open_cold_form)          # NUEVO

        self.btn_docs.clicked.connect(self._open_documents)

        # Añadir al layout
        for w in (
            lbl_user, btn_mod1, btn_mod2, btn_mod3,
            *self.mod1_btns, *self.mod2_btns, *self.mod3_btns,
            self.btn_docs,
        ):
            s_lay.addWidget(w)
        s_lay.addStretch()

        # ---------------- Pestaña Clientes ---------------
        self.tabs = QTabWidget()
        self._init_tab_clients()

        container = QWidget()
        main_lay = QHBoxLayout(container)
        main_lay.addWidget(sidebar, 1)
        main_lay.addWidget(self.tabs, 4)
        self.setCentralWidget(container)

    # ==================================================== #
    # Cambio de módulo                                     #
    # ==================================================== #
    def _switch_module(self, n: int):
        for b in self.mod1_btns + self.mod2_btns + self.mod3_btns:
            b.hide()
        if n == 1:
            for b in self.mod1_btns:
                b.show()
        elif n == 2:
            for b in self.mod2_btns:
                b.show()
        else:
            for b in self.mod3_btns:
                b.show()
        self.tabs.setCurrentIndex(0)

    # ==================================================== #
    # TAB CLIENTES                                         #
    # ==================================================== #
    def _init_tab_clients(self):
        tab = QWidget()
        lay = QVBoxLayout(tab)

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

    # ==================================================== #
    # Slots / helpers                                      #
    # ==================================================== #
    def _row_changed(self, current, _prev):
        has_client = current.isValid()
        self.btn_docs.setEnabled(has_client)
        for b in self.mod1_btns + self.mod2_btns + self.mod3_btns:
            if b.isVisible():
                b.setEnabled(has_client)

    def _current_client(self):
        ix = self.table.currentIndex()
        return self.model.client_at(ix.row()) if ix.isValid() else None

    # ---------- Formularios Genéricos ----------
    def _open_if_client(self, FormCls):
        client = self._current_client()
        if client:
            FormCls(client, self).exec()

    # ---------- Módulo 1 ----------
    def _open_intake_form(self):
        if IntakeForm(self).exec() == IntakeForm.Accepted:
            self._load_clients()

    def _double_click_client(self, ix: QModelIndex):
        self._open_if_client(BrandCanvasForm)

    def _open_documents(self):
        self._open_if_client(DocumentListDialog)

    def _open_sector_form(self):   self._open_if_client(SectorForm)
    def _open_linkedin_form(self): self._open_if_client(LinkedInForm)
    def _open_interview_form(self):self._open_if_client(InterviewForm)
    def _open_strategy_form(self): self._open_if_client(BrandStrategyForm)
    def _open_calendar_form(self): self._open_if_client(ContentPlanForm)
    def _open_network_form(self):  self._open_if_client(NetworkingForm)
    def _open_kpi_form(self):      self._open_if_client(KPIForm)
    def _open_image_form(self):    self._open_if_client(ImageForm)

    # ---------- Módulo 2 ----------
    def _open_cv_form(self):       self._open_if_client(CVForm)
    def _open_ats_form(self):      self._open_if_client(ATSForm)
    def _open_cold_form(self):     self._open_if_client(ColdMessageForm)

    def _open_search_form(self):
        client = self._current_client()
        if client:
            from employ_toolkit.gui.forms.search_form import SearchForm
            SearchForm(client, self).exec()

# ------------------------- Debug ------------------------- #
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    win = MainWindow("demo", "consultor")
    win.show()
    sys.exit(app.exec())
