# employ_toolkit/gui/forms/ats_form.py
"""
ATS & Plataformas de Empleo
---------------------------
• Lista de portales a la izquierda
• “LinkedIn” → formulario guiado (Headline, About, Skills…)
• Resto de portales → plantilla estructurada (Información personal, etc.)
• «Guardar» almacena los datos en memoria
• «Exportar Guía PDF» crea el PDF y lo registra en Documentos (mód. 2)
"""

from datetime import date
from typing import Dict, Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QListWidget, QPushButton, QHBoxLayout, QVBoxLayout,
    QMessageBox, QStackedWidget
)

from employ_toolkit.gui.forms.linkedin_widget import LinkedInWidget
from employ_toolkit.gui.forms.generic_ats_widget import GenericATSWidget   # 🆕
from employ_toolkit.modules.ats_guides import generate_ats_pdf
from employ_toolkit.core.storage import get_session
from employ_toolkit.core.models import Document

PLATFORMS = [
    "LinkedIn",                                  # 🔗 Perfil top
    "Indeed – multisectorial",                   #
    "Greenhouse – tech-startups (ATS)",          #
    "Workday – corporativo / enterprise (ATS)",  #
    "Lever – SaaS / tech (ATS)",                 #
    "Monster – generalista",                     #
    "GitHub Jobs – dev",                         #
    "StackOverflow Jobs – dev",                  #
    "OCC – MX generalista",                      #
    "CompuTrabajo – LatAm generalista",          #
    "torre.ai – remote / tech",                  #
    "elempleo.com – CO generalista",             #
]

class ATSForm(QDialog):
    """Ventana para capturar y exportar perfiles de portales/ATS."""

    def __init__(self, client, parent=None):
        super().__init__(parent)
        self.client = client
        self.setWindowTitle(f"ATS & Plataformas – {client.full_name}")
        self.resize(900, 540)
        self.setMinimumSize(760, 440)

        # ---------------- datos en memoria ----------------
        self.data: Dict[str, Any] = {}      # {portal: dict | str}

        # ---------------- widgets -------------------------
        self.list = QListWidget()
        self.list.addItems(PLATFORMS)
        self.list.currentTextChanged.connect(self._load_platform)

        self.linked  = LinkedInWidget()     # formulario guiado LinkedIn
        self.generic = GenericATSWidget()   # plantilla Info personal, etc.

        self.stack = QStackedWidget()
        self.stack.addWidget(self.generic)  # idx 0
        self.stack.addWidget(self.linked)   # idx 1

        btn_save   = QPushButton("Guardar plataforma")
        btn_export = QPushButton("Exportar Guía PDF")
        btn_save.clicked.connect(self._save_current)
        btn_export.clicked.connect(self._export_pdf)

        # --------------- layout ---------------------------
        left  = QVBoxLayout(); left.addWidget(self.list)

        right = QVBoxLayout()
        right.addWidget(self.stack, 1)
        right.addWidget(btn_save)
        right.addWidget(btn_export)

        main = QHBoxLayout(self)
        main.addLayout(left, 1)
        main.addLayout(right, 2)

        # carga inicial
        self.list.setCurrentRow(0)

    # ==================================================== #
    # CARGAR / MOSTRAR                                     #
    # ==================================================== #
    def _load_platform(self, display_name: str) -> None:
        """Muestra los datos guardados del portal seleccionado."""
        name = display_name.split(" – ")[0]          # extrae nombre base
        if name == "LinkedIn":
            self.stack.setCurrentWidget(self.linked)
            data = self.data.get("LinkedIn", {})
            fields = (
                ("headline", self.linked.headline, str),
                ("about",    self.linked.about,    "plain"),
                ("skills",   self.linked.skills,   "plain"),
                ("exp",      self.linked.exp,      "plain"),
                ("banner",   self.linked.banner,   str),
                ("edu",      self.linked.edu,      "plain"),
                ("cert",     self.linked.cert,     "plain"),
                ("lang",     self.linked.lang,     "plain"),
            )
            for key, widget, mode in fields:
                val = data.get(key, "")
                if mode == "plain":
                    widget.setPlainText(val)
                else:
                    widget.setText(val)
        else:
            self.stack.setCurrentWidget(self.generic)
            self.generic.from_dict(self.data.get(name, {}))

    # ==================================================== #
    # GUARDAR EN MEMORIA                                   #
    # ==================================================== #
    def _save_current(self) -> None:
        display_name = self.list.currentItem().text()
        name = display_name.split(" – ")[0]
        if name == "LinkedIn":
            self.data["LinkedIn"] = {
                "headline": self.linked.headline.text().strip(),
                "about":    self.linked.about.toPlainText().strip(),
                "skills":   self.linked.skills.toPlainText().strip(),
                "exp":      self.linked.exp.toPlainText().strip(),
                "banner":   self.linked.banner.text().strip(),
                "edu":      self.linked.edu.toPlainText().strip(),
                "cert":     self.linked.cert.toPlainText().strip(),
                "lang":     self.linked.lang.toPlainText().strip(),
            }
        else:
            self.data[name] = self.generic.to_dict()

        QMessageBox.information(self, "Guardado",
                                f"{name} almacenado correctamente.")

    # ==================================================== #
    # EXPORTAR PDF                                         #
    # ==================================================== #
    def _export_pdf(self) -> None:
        if not self.data:
            QMessageBox.warning(self, "Sin datos",
                                 "Agrega y guarda al menos una plataforma.")
            return

        pdf_path = generate_ats_pdf(self.client, self.data)

        # registrar en Documentos
        with get_session() as s:
            s.add(Document(
                client_id=self.client.id, module=2,
                doc_type="ats_pdf", path=str(pdf_path),
                created_at=date.today(),
            ))
            s.commit()

        QMessageBox.information(self, "PDF creado",
                                f"Guía exportada: {pdf_path.name}")
        self.accept()
