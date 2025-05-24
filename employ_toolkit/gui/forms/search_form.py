# employ_toolkit/gui/forms/search_form.py
"""
Técnicas de búsqueda de ofertas
-------------------------------
• QListWidget a la izquierda con el nombre de la técnica.
• Al hacer clic se muestra:
    – Descripción detallada (QTextBrowser – solo lectura)
    – “Adaptación para el cliente” (QTextEdit editable)
• Guardar → se almacena en self.notes
• Exportar PDF → genera informe y lo registra en Document.
"""

from pathlib import Path
from datetime import date
import uuid
from typing import Dict

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QListWidget, QTextBrowser, QTextEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QSplitter, QWidget
)

from employ_toolkit.modules.search_guide import generate_search_pdf
from employ_toolkit.core.storage import get_session
from employ_toolkit.core.models import Document

# ===================== Catálogo de técnicas ====================== #
SEARCH_TECHNIQUES: Dict[str, str] = {
    "Búsqueda Boolean avanzada":
        """Cómo usar operadores AND / OR / NOT y comillas para refinar
la búsqueda en Google, LinkedIn o portales de empleo.  
Ejemplo:  
    ("data engineer" OR "ingeniero de datos") AND (Python OR SQL) AND
    NOT (senior OR lead)""",

    "Alertas automáticas en Google & LinkedIn":
        """Paso 1: crea la query boolean y pruébala.  
Paso 2: ve a google.com/alerts, pega la query, elige
    – Frecuencia  
    – Idioma  
    – Región  
y guarda la alerta.  
En LinkedIn Jobs: configura “Job alert” con filtros de cargo, ubicación y
salario, activa notificaciones por correo.""",

    "Networking pro-activo (referrals)":
        """1 › Identifica empleados en la empresa objetivo (LinkedIn “People”).  
2 › Conéctate con un mensaje corto.  
3 › Tras aceptar, solicita amable referencia adjuntando tu CV
optimizado y resaltando el valor para el rol.""",

    "Uso de filtros en portales especializados":
        """Ej.: GitHub Jobs / StackOverflow → filtra por lenguaje,
localización ‘remote’, etiqueta ‘beginners-friendly’.  
Guarda la URL y revísala a diario con la técnica Pomodoro (25 min).""",

    "Método ‘Dream-100’":
        """Haz una lista de tus 100 empresas ideales.  
Para cada una:
    • Sigue su página de LinkedIn  
    • Activa ‘Company Notifications’  
    • Suscríbete a su RSS / newsletter  
    • Conecta con al menos 2 personas clave""",

    "Mapa de contactos en 2º grado":
        """Exporta tus contactos de 1º grado en CSV (LinkedIn settings).  
Usa Excel para cruzar empresa/puesto.  
Diseña mensajes personalizados solicitando introducción
al contacto de 2º grado.""",
}

# ================================================================= #
class SearchForm(QDialog):
    def __init__(self, client, parent=None):
        super().__init__(parent)
        self.client = client
        self.setWindowTitle(f"Técnicas de Búsqueda – {client.full_name}")
        self.resize(900, 520)

        self.notes: Dict[str, str] = {}       # {técnica: adaptación}

        # ---------- widgets ----------
        self.list = QListWidget()
        self.list.addItems(SEARCH_TECHNIQUES.keys())
        self.list.currentTextChanged.connect(self._load_technique)

        self.desc = QTextBrowser()            # explicación paso a paso
        self.desc.setOpenExternalLinks(True)

        self.edit = QTextEdit()               # adaptación / notas
        self.edit.setPlaceholderText("Escribe aquí cómo aplicará el cliente esta técnica…")

        btn_save   = QPushButton("Guardar nota")
        btn_export = QPushButton("Exportar PDF guía")
        btn_save.clicked.connect(self._save_current)
        btn_export.clicked.connect(self._export_pdf)

        # ---------- layout ----------
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.desc)
        splitter.addWidget(self.edit)
        splitter.setSizes([260, 220])         # proporción inicial

        right = QVBoxLayout()
        right.addWidget(splitter, 1)
        right.addWidget(btn_save)
        right.addWidget(btn_export)

        lay = QHBoxLayout(self)
        lay.addWidget(self.list, 1)
        lay.addLayout(right, 2)

        self.list.setCurrentRow(0)            # carga inicial

    # -------------------------------------------------------------- #
    def _load_technique(self, name: str):
        """Muestra descripción y nota guardada (si existe)."""
        self.desc.setMarkdown(SEARCH_TECHNIQUES[name])
        self.edit.setPlainText(self.notes.get(name, ""))

    def _save_current(self):
        name = self.list.currentItem().text()
        self.notes[name] = self.edit.toPlainText().strip()
        QMessageBox.information(self, "Guardado", f"Nota para «{name}» almacenada.")

    # -------------------------------------------------------------- #
    def _export_pdf(self):
        if not self.notes:
            QMessageBox.warning(self, "Sin notas",
                                 "Añade al menos una técnica con su adaptación.")
            return
        pdf_path = generate_search_pdf(self.client, self.notes)

        # registrar
        from employ_toolkit.core.storage import get_session  # import perezoso
        with get_session() as s:
            s.add(Document(
                client_id=self.client.id, module=2,
                doc_type="search_guide_pdf",
                path=str(pdf_path), created_at=date.today()))
            s.commit()

        QMessageBox.information(self, "PDF creado", f"Guía exportada: {pdf_path.name}")
        self.accept()
