# employ_toolkit/gui/forms/disc_comp_form.py
"""
Competencias DISC  –  Módulo 3-B
--------------------------------
• El consultor selecciona la categoría primaria y secundaria del DISC.
• Para cada categoría se muestran 5 competencias clave (check-box).
• Se pueden Añadir, Editar y Eliminar competencias en tiempo real.
• «Exportar PDF» genera un informe con ÚNICAMENTE las competencias
  marcadas y registra el documento en la tabla documents (mód. 3).
"""

from datetime import date
from pathlib import Path
import uuid

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QComboBox, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QTextEdit, QHBoxLayout, QVBoxLayout,
    QMessageBox, QInputDialog, QWidget
)

from employ_toolkit.modules.disc_comp import generate_disc_comp_pdf
from employ_toolkit.core.storage import get_session
from employ_toolkit.core.models import Document

# --- Tabla base de competencias ------------------------------------------ #
BASE_COMP = {
    "D": [
        ("Orientación a Resultados",
         "Fijar metas ambiciosas y alcanzarlas con determinación."),
        ("Decisión",
         "Tomar decisiones ágiles incluso bajo presión."),
        ("Iniciativa",
         "Actuar proactivamente sin esperar indicaciones."),
        ("Asunción de Riesgos",
         "Aceptar retos calculados para lograr ventajas competitivas."),
        ("Autoridad",
         "Guiar al equipo estableciendo dirección clara.")
    ],
    "I": [
        ("Influencia",
         "Persuadir e inspirar a otros con entusiasmo."),
        ("Networking",
         "Construir y mantener relaciones de valor."),
        ("Comunicación Verbal",
         "Expresar ideas con seguridad y energía."),
        ("Creatividad",
         "Generar ideas innovadoras ante desafíos."),
        ("Empatía Social",
         "Leer emociones para conectar con la audiencia.")
    ],
    "S": [
        ("Colaboración",
         "Trabajar armónicamente buscando consenso."),
        ("Paciencia",
         "Mantener calma y constancia ante la presión."),
        ("Escucha Activa",
         "Prestar atención genuina a las necesidades de otros."),
        ("Fiabilidad",
         "Cumplir compromisos de forma consistente."),
        ("Apoyo",
         "Ofrecer ayuda y mentoring a compañeros.")
    ],
    "C": [
        ("Análisis",
         "Examinar datos con rigurosidad y lógica."),
        ("Precisión",
         "Garantizar calidad y exactitud en la entrega."),
        ("Planificación",
         "Estructurar tareas con criterios claros y plazos realistas."),
        ("Cumplimiento Normativo",
         "Asegurar adherencia a políticas y estándares."),
        ("Pensamiento Crítico",
         "Cuestionar suposiciones y validar hipótesis objetivamente.")
    ],
}

OUTPUT_DIR = Path("workspace")
OUTPUT_DIR.mkdir(exist_ok=True)


# ------------------------------------------------------------------------- #
class DISCCompForm(QDialog):
    """Ventana para configurar competencias DISC y exportar el PDF."""

    def __init__(self, client, parent=None):
        super().__init__(parent)
        self.client = client
        self.setWindowTitle(f"Competencias DISC – {client.full_name}")
        self.resize(920, 540)

        # ======= Selección de categorías ======= #
        self.cmb_primary   = QComboBox()
        self.cmb_secondary = QComboBox()
        for c in ["D", "I", "S", "C"]:
            self.cmb_primary.addItem(c)
            self.cmb_secondary.addItem(c)
        self.cmb_primary.currentTextChanged.connect(self._load_lists)
        self.cmb_secondary.currentTextChanged.connect(self._load_lists)

        # ======= Listas de competencias ======= #
        self.lst_primary   = QListWidget()
        self.lst_secondary = QListWidget()
        for lst in (self.lst_primary, self.lst_secondary):
            lst.setSelectionMode(QListWidget.SingleSelection)

        # ======= Botoneras de A/E/D ======= #
        self._make_crud_buttons()

        # ======= Exportar ======= #
        btn_pdf = QPushButton("Exportar PDF")
        btn_pdf.clicked.connect(self._export_pdf)

        # ======= Layout ======= #
        top_sel = QHBoxLayout()
        top_sel.addWidget(QLabel("Categoría 1 (dominante):")); top_sel.addWidget(self.cmb_primary)
        top_sel.addSpacing(30)
        top_sel.addWidget(QLabel("Categoría 2:"));             top_sel.addWidget(self.cmb_secondary)

        col_left = QVBoxLayout()
        col_left.addWidget(QLabel("Competencias categoría 1", alignment=Qt.AlignCenter))
        col_left.addWidget(self.lst_primary, 1)
        col_left.addLayout(self.crud_left)

        col_right = QVBoxLayout()
        col_right.addWidget(QLabel("Competencias categoría 2", alignment=Qt.AlignCenter))
        col_right.addWidget(self.lst_secondary, 1)
        col_right.addLayout(self.crud_right)

        lists = QHBoxLayout(); lists.addLayout(col_left); lists.addLayout(col_right)

        root = QVBoxLayout(self)
        root.addLayout(top_sel)
        root.addLayout(lists, 1)
        root.addWidget(btn_pdf, alignment=Qt.AlignRight)

        # Diccionarios dinámicos {categoria: {nombre: defin}}
        self.data = {k: {n: d for n, d in BASE_COMP[k]} for k in BASE_COMP}
        self._load_lists()  # cargar inicial

    # ------------------------------------------------------------------ #
    # Helpers CRUD                                                       #
    # ------------------------------------------------------------------ #
    def _make_crud_buttons(self):
        def crud_box(target_list: QListWidget, cat_fn):
            btn_add = QPushButton("➕ Añadir")
            btn_edit= QPushButton("✏️ Editar")
            btn_del = QPushButton("🗑 Eliminar")
            btn_add.clicked.connect(lambda: self._add_comp(target_list, cat_fn()))
            btn_edit.clicked.connect(lambda: self._edit_comp(target_list, cat_fn()))
            btn_del.clicked.connect(lambda: self._del_comp(target_list, cat_fn()))
            box = QHBoxLayout(); box.addWidget(btn_add); box.addWidget(btn_edit); box.addWidget(btn_del); box.addStretch()
            return box

        self.crud_left  = crud_box(self.lst_primary,   lambda: self.cmb_primary.currentText())
        self.crud_right = crud_box(self.lst_secondary, lambda: self.cmb_secondary.currentText())

    def _add_comp(self, lst: QListWidget, cat: str):
        text, ok = QInputDialog.getMultiLineText(
            self, "Nueva competencia",
            "Escribe «Nombre: Definición»\n(ej. Gestión de Cambios: Capacidad de...):"
        )
        if ok and ":" in text:
            name, desc = [t.strip() for t in text.split(":", 1)]
            self.data[cat][name] = desc
            self._refresh_list(lst, cat)
        elif ok:
            QMessageBox.warning(self, "Formato", "Separa nombre y definición con ':'.")

    def _edit_comp(self, lst: QListWidget, cat: str):
        item = lst.currentItem()
        if not item:
            return
        name = item.data(Qt.UserRole)
        current = f"{name}: {self.data[cat][name]}"
        text, ok = QInputDialog.getMultiLineText(
            self, "Editar competencia", "Modifica nombre y/o definición:", current
        )
        if ok and ":" in text:
            new_name, new_desc = [t.strip() for t in text.split(":", 1)]
            del self.data[cat][name]
            self.data[cat][new_name] = new_desc
            self._refresh_list(lst, cat)
        elif ok:
            QMessageBox.warning(self, "Formato", "Separa nombre y definición con ':'.")

    def _del_comp(self, lst: QListWidget, cat: str):
        item = lst.currentItem()
        if not item:
            return
        name = item.data(Qt.UserRole)
        reply = QMessageBox.question(
            self, "Confirmar", f"¿Eliminar «{name}»?", QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            del self.data[cat][name]
            self._refresh_list(lst, cat)

    # ------------------------------------------------------------------ #
    # Cargar / refrescar listas                                          #
    # ------------------------------------------------------------------ #
    def _refresh_list(self, lst: QListWidget, cat: str):
        lst.blockSignals(True)
        lst.clear()
        for name, desc in self.data[cat].items():
            item = QListWidgetItem(f"{name}: {desc}")
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            item.setData(Qt.UserRole, name)
            lst.addItem(item)
        lst.blockSignals(False)

    def _load_lists(self):
        self._refresh_list(self.lst_primary,   self.cmb_primary.currentText())
        self._refresh_list(self.lst_secondary, self.cmb_secondary.currentText())

    # ------------------------------------------------------------------ #
    # Exportar PDF                                                       #
    # ------------------------------------------------------------------ #
    def _export_pdf(self):
        sel_primary = self._selected_items(self.lst_primary,   self.cmb_primary.currentText())
        sel_secondary = self._selected_items(self.lst_secondary, self.cmb_secondary.currentText())

        if not sel_primary and not sel_secondary:
            QMessageBox.warning(self, "Nada marcado",
                                 "Marca al menos una competencia en cualquiera de las listas.")
            return

        pdf_path = generate_disc_comp_pdf(
            self.client,
            self.cmb_primary.currentText(),   sel_primary,
            self.cmb_secondary.currentText(), sel_secondary
        )

        with get_session() as s:
            s.add(Document(
                client_id=self.client.id, module=3,
                doc_type="disc_competencies", path=str(pdf_path),
                created_at=date.today()
            ))
            s.commit()

        QMessageBox.information(self, "PDF creado",
                                f"Informe exportado: {pdf_path.name}")
        self.accept()

    # ------------------------------------------------------------------ #
    @staticmethod
    def _selected_items(lst: QListWidget, cat: str):
        comps = {}
        for i in range(lst.count()):
            it = lst.item(i)
            if it.checkState() == Qt.Checked:
                name = it.data(Qt.UserRole)
                # El texto visual ya es «name: desc», pero preferimos limpiar
                desc = it.text().split(":", 1)[1].strip()
                comps[name] = desc
        return comps
