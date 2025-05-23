# employ_toolkit/gui/main.py
"""
Ventana Principal
-----------------
• Tabla de clientes, botón “Nuevo”.
• Doble-clic → BrandCanvas.
• Botones por módulo (se muestran al pulsar Módulo 1/2/3).
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

# Formularios
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

# --------------------------------------------------------------------------- #
# Modelo de tabla                                                             #
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
# Main Window                                                                 #
# --------------------------------------------------------------------------- #
class MainWindow(QMainWindow):
    def __init__(self, username: str, role: str):
        super().__init__()
        self.setWindowTitle("Plataforma de Empleabilidad")
        self.resize(1050, 670)

        # ---------------- Barra lateral ----------------
        sidebar = QWidget(); s_lay = QVBoxLayout(sidebar)

        lbl_user = QLabel(f"👤 {username} ({role})", alignment=Qt.AlignCenter)
        lbl_user.setFont(QFont("Arial", 10, QFont.Bold))

        # Selector de módulo
        btn_mod1 = QPushButton("Módulo 1 · Diagnóstico & Marca")
        btn_mod2 = QPushButton("Módulo 2 · Presencia Digital")
        btn_mod3 = QPushButton("Módulo 3 · Skills & Selección")
        btn_mod1.clicked.connect(partial(self._switch_module, 1))
        btn_mod2.clicked.connect(partial(self._switch_module, 2))
        btn_mod3.clicked.connect(partial(self._switch_module, 3))

        # -------- Botones de acciones -------- #
        # Módulo 1
        self.btn_linkedin  = QPushButton("🔗 Perfil LinkedIn")
        self.btn_sector    = QPushButton("📊 Sector & Mercado")
        self.btn_strategy  = QPushButton("📑 Estrategia Marca")
        self.btn_calendar  = QPushButton("📅 Parrilla Contenido")
        self.btn_network   = QPushButton("🤝 Networking")
        self.btn_kpis      = QPushButton("📈 KPIs")
        self.btn_image     = QPushButton("🖼️ Imagen Prof.")
        self.btn_interview = QPushButton("📝 Entrevista")

        # Módulo 2
        self.btn_cv = QPushButton("📄 CV Optimizado")
        self.btn_ats  = QPushButton("🌐 ATS & Plataformas")  

        # Módulo 3 (vacío por ahora)
        self.mod3_btns: List[QPushButton] = []

        # Documentos (visible siempre)
        self.btn_docs = QPushButton("📂 Documentos del Cliente")

        # Agrupar visibilidad
        self.mod1_btns: List[QPushButton] = [
            self.btn_linkedin, self.btn_sector, self.btn_strategy,
            self.btn_calendar, self.btn_network, self.btn_kpis,
            self.btn_image, self.btn_interview
        ]
        self.mod2_btns: List[QPushButton] = [self.btn_cv, self.btn_ats]

        # Ocultar M2 y M3 al inicio
        for b in self.mod2_btns + self.mod3_btns:
            b.hide()

        # ------- Conexiones de acciones -------
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

        container = QWidget(); main_lay = QHBoxLayout(container)
        main_lay.addWidget(sidebar, 1); main_lay.addWidget(self.tabs, 4)
        self.setCentralWidget(container)

    # ---------------- Cambio de módulo ---------------- #
    def _switch_module(self, n: int):
        """Muestra sólo los botones del módulo seleccionado."""
        for b in self.mod1_btns + self.mod2_btns + self.mod3_btns:
            b.hide()
        if n == 1:
            for b in self.mod1_btns: b.show()
        elif n == 2:
            for b in self.mod2_btns: b.show()
        else:
            for b in self.mod3_btns: b.show()
        self.tabs.setCurrentIndex(0)

    # ----------------- TAB Clientes ------------------- #
    def _init_tab_clients(self):
        tab = QWidget(); lay = QVBoxLayout(tab)

        btn_new = QPushButton("➕ Nuevo Cliente")
        btn_new.clicked.connect(self._open_intake_form)

        self.table = QTableView()
        self._load_clients()
        self.table.doubleClicked.connect(self._double_click_client)
        self.table.selectionModel().currentRowChanged.connect(self._row_changed)

        lay.addWidget(btn_new); lay.addWidget(self.table)
        self.tabs.addTab(tab, "Clientes")

    def _load_clients(self):
        with get_session() as s:
            data = s.exec(select(Client).order_by(Client.id.desc())).all()
        self.model = ClientTableModel(data)
        self.table.setModel(self.model)
        self.table.resizeColumnsToContents()

    # ------------------- Slots ------------------- #
    def _row_changed(self, current, _prev):
        has_client = current.isValid()
        # Docs siempre visible, depende sólo de selección
        self.btn_docs.setEnabled(has_client)
        # Habilitar botones visibles del módulo activo
        for b in self.mod1_btns + self.mod2_btns + self.mod3_btns:
            if b.isVisible():
                b.setEnabled(has_client)

    def _current_client(self):
        idx = self.table.currentIndex()
        return self.model.client_at(idx.row()) if idx.isValid() else None

    # -------------- Formularios -------------- #
    def _open_intake_form(self):
        if IntakeForm(self).exec() == IntakeForm.Accepted:
            self._load_clients()

    def _double_click_client(self, idx: QModelIndex):
        client = self.model.client_at(idx.row())
        if BrandCanvasForm(client, self).exec() == BrandCanvasForm.Accepted:
            QMessageBox.information(self, "Documento guardado",
                                    "BrandCanvas registrado.")
            self._row_changed(idx, None)

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

    def _open_cv_form(self):
        client = self._current_client()
        if client:
            CVForm(client, self).exec()

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

    def _open_image_form(self):
        client = self._current_client()
        if client:
            ImageForm(client, self).exec()
    
    def _open_ats_form(self):                                    # ← NUEVO
        client = self._current_client()
        if client:
            ATSForm(client, self).exec()


# ---------------------------- Debug ---------------------------- #
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    win = MainWindow("demo", "consultor")
    win.show()
    sys.exit(app.exec())
