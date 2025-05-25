# employ_toolkit/gui/forms/skills_matrix_form.py
"""
Skill Matrix – Módulo 3-A
-------------------------
• Hard skills (check-list) con plataforma sugerida.
• Soft skills (check-list) con definición editable.
• Botones ➕ / ✖️ para añadir o eliminar la skill seleccionada.
• «Exportar PDF» genera informe SOLO con las skills marcadas.
"""
from pathlib import Path
from datetime import date
import uuid
import re                                      # ← para extraer plataforma

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QListWidget, QListWidgetItem, QTextEdit,
    QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QWidget,
    QMessageBox, QInputDialog
)

from employ_toolkit.modules.skills_matrix import generate_skill_matrix_pdf
from employ_toolkit.core.storage import get_session
from employ_toolkit.core.models import Document

# ---------- Catálogos iniciales ---------------------------------- #
HARD_SKILLS = [
    ("Python / Data Science", "Coursera"),
    ("Cloud Computing (AWS)", "AWS Skill Builder"),
    ("Cybersecurity Basics",  "edX"),
    ("Salesforce CRM",        "Trailhead"),
    ("Digital Marketing",     "Google Skillshop"),
    ("SQL & Data Engineering","DataCamp"),
    ("Project Management",    "Coursera"),
    ("UI/UX Design (Figma)",  "Udemy"),
    ("Power BI Analytics",    "LinkedIn Learning"),
    ("AI Prompt Engineering", "DeepLearning.AI"),
    ("Kubernetes DevOps",     "Udacity"),
    ("Java (Spring)",         "Pluralsight"),
    ("SAP S/4 HANA",          "openSAP"),
    ("Excel Avanzado",        "LinkedIn Learning"),
    ("RPA (UiPath)",          "UiPath Academy"),
    ("Docker Containers",     "Udemy"),
    ("React.js Frontend",     "Codecademy"),
    ("Node.js Backend",       "freeCodeCamp"),
    ("QA Automation (Selenium)","Udemy"),
    ("Graphic Design (Adobe)", "Adobe Learn"),
]

SOFT_SKILLS = [
    ("Comunicación Efectiva",
     "Transmitir ideas con claridad y adaptarse al interlocutor."),
    ("Trabajo en Equipo",
     "Colaborar con otros para alcanzar objetivos comunes."),
    ("Pensamiento Crítico",
     "Analizar información para tomar decisiones fundamentadas."),
    ("Resolución de Problemas",
     "Identificar causas raíz y proponer soluciones prácticas."),
    ("Adaptabilidad",
     "Ajustarse rápidamente a cambios y nuevos retos."),
    ("Gestión del Tiempo",
     "Priorizar tareas para cumplir plazos."),
    ("Liderazgo",
     "Motivar y guiar a un grupo hacia resultados."),
    ("Orientación al Cliente",
     "Comprender y satisfacer necesidades del cliente."),
    ("Creatividad",
     "Generar ideas innovadoras y originales."),
    ("Inteligencia Emocional",
     "Reconocer y gestionar emociones propias y ajenas."),
]

# ----------------------------------------------------------------- #
class SkillsMatrixForm(QDialog):
    def __init__(self, client, parent=None):
        super().__init__(parent)
        self.client = client
        self.setWindowTitle(f"Skill Matrix – {client.full_name}")
        self.resize(880, 540)

        # -------- Hard skills (check-list) ------------------------ #
        self.lst_hard = QListWidget()
        self.lst_hard.setSelectionMode(QListWidget.SingleSelection)
        for skill, platform in HARD_SKILLS:
            self._add_hard_item(skill, platform, checked=False)

        lbl_hard = QLabel("Hard Skills (selecciona):", alignment=Qt.AlignCenter)

        # -------- Soft skills (check-list + definición) ----------- #
        self.lst_soft = QListWidget()
        self.lst_soft.setSelectionMode(QListWidget.SingleSelection)
        for skill, _ in SOFT_SKILLS:
            self._add_soft_item(skill, checked=False)

        self.lst_soft.currentRowChanged.connect(self._load_definition)

        self.txt_def = QTextEdit()
        self.txt_def.setPlaceholderText("Definición / descripción operativa…")
        self.txt_def.textChanged.connect(self._save_definition)

        lbl_soft = QLabel("Soft Skills (marca y edita):", alignment=Qt.AlignCenter)

        # ---------- Botones barra inferior ------------------------ #
        btn_add_hard = QPushButton("➕ Hard Skill")
        btn_del_hard = QPushButton("✖️ Eliminar")
        btn_add_soft = QPushButton("➕ Soft Skill")
        btn_del_soft = QPushButton("✖️ Eliminar")
        btn_pdf      = QPushButton("Exportar PDF")

        btn_add_hard.clicked.connect(self._add_hard_skill)
        btn_del_hard.clicked.connect(self._delete_hard_skill)
        btn_add_soft.clicked.connect(self._add_soft_skill)
        btn_del_soft.clicked.connect(self._delete_soft_skill)
        btn_pdf.clicked.connect(self._export_pdf)

        # ---------- Layouts -------------------------------------- #
        col_hard = QVBoxLayout()
        col_hard.addWidget(lbl_hard)
        col_hard.addWidget(self.lst_hard)

        col_soft = QVBoxLayout()
        col_soft.addWidget(lbl_soft)
        col_soft.addWidget(self.lst_soft)
        col_soft.addWidget(self.txt_def)

        columns = QHBoxLayout()
        columns.addLayout(col_hard, 1)
        columns.addLayout(col_soft, 1)

        row_btns = QHBoxLayout()
        row_btns.addWidget(btn_add_hard)
        row_btns.addWidget(btn_del_hard)
        row_btns.addSpacing(20)
        row_btns.addWidget(btn_add_soft)
        row_btns.addWidget(btn_del_soft)
        row_btns.addStretch()
        row_btns.addWidget(btn_pdf)

        main = QVBoxLayout(self)
        main.addLayout(columns, 1)
        main.addLayout(row_btns)

        # Diccionario editable: soft skill -> definición
        self.soft_defs = {s: d for s, d in SOFT_SKILLS}

    # ============================================================ #
    # Utilidades de item list                                      #
    # ============================================================ #
    def _add_hard_item(self, skill: str, platform: str, checked=True):
        text = f"{skill}  ({platform})"
        item = QListWidgetItem(text)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Checked if checked else Qt.Unchecked)
        self.lst_hard.addItem(item)

    def _add_soft_item(self, skill: str, checked=True):
        item = QListWidgetItem(skill)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Checked if checked else Qt.Unchecked)
        self.lst_soft.addItem(item)

    # ============================================================ #
    # Soft skill – carga / guarda definición                       #
    # ============================================================ #
    def _load_definition(self, row: int):
        self.txt_def.blockSignals(True)
        self.txt_def.setPlainText(
            "" if row < 0 else self.soft_defs.get(self.lst_soft.item(row).text(), "")
        )
        self.txt_def.blockSignals(False)

    def _save_definition(self):
        row = self.lst_soft.currentRow()
        if row >= 0:
            skill = self.lst_soft.item(row).text()
            self.soft_defs[skill] = self.txt_def.toPlainText().strip()

    # ============================================================ #
    # Alta y eliminación de skills                                 #
    # ============================================================ #
    def _add_hard_skill(self):
        text, ok = QInputDialog.getText(
            self, "Nueva Hard Skill",
            "Escribe la skill y la plataforma entre paréntesis:\n"
            "Ej.:  GoLang Backend (Udemy)"
        )
        if ok and text.strip():
            m = re.match(r"(.+?)\s*\((.+)\)", text.strip())
            if not m:
                QMessageBox.warning(self, "Formato incorrecto",
                                    "Debes incluir la plataforma entre paréntesis.")
                return
            skill, platform = m.group(1).strip(), m.group(2).strip()
            self._add_hard_item(skill, platform, checked=True)

    def _add_soft_skill(self):
        skill, ok = QInputDialog.getText(
            self, "Nueva Soft Skill", "Nombre de la soft skill:"
        )
        if not (ok and skill.strip()):
            return
        definition, ok = QInputDialog.getMultiLineText(
            self, "Definición", f"Define «{skill.strip()}»:"
        )
        if ok:
            clean = skill.strip()
            self._add_soft_item(clean, checked=True)
            self.soft_defs[clean] = definition.strip()

    def _delete_hard_skill(self):
        row = self.lst_hard.currentRow()
        if row >= 0:
            self.lst_hard.takeItem(row)

    def _delete_soft_skill(self):
        row = self.lst_soft.currentRow()
        if row >= 0:
            skill = self.lst_soft.item(row).text()
            self.lst_soft.takeItem(row)
            self.soft_defs.pop(skill, None)
            self.txt_def.clear()

    # ============================================================ #
    # Exportar PDF                                                 #
    # ============================================================ #
    def _export_pdf(self):
        # ---- Hard seleccionado (skill, plataforma) ----
        hard_sel = []
        for i in range(self.lst_hard.count()):
            item = self.lst_hard.item(i)
            if item.checkState() == Qt.Checked:
                # «Skill  (Plataforma)»
                m = re.match(r"(.+?)\s*\((.+)\)$", item.text())
                if m:
                    hard_sel.append((m.group(1).strip(), m.group(2).strip()))
                else:
                    hard_sel.append((item.text(), ""))

        # ---- Soft seleccionado {skill: definición} ----
        soft_sel = {
            self.lst_soft.item(i).text(): self.soft_defs.get(self.lst_soft.item(i).text(), "")
            for i in range(self.lst_soft.count())
            if self.lst_soft.item(i).checkState() == Qt.Checked
        }

        if not hard_sel and not soft_sel:
            QMessageBox.warning(self, "Nada seleccionado",
                                "Marca al menos una hard o soft skill.")
            return

        pdf = generate_skill_matrix_pdf(self.client, soft_sel, hard_sel)

        # registrar en Documentos
        with get_session() as s:
            s.add(Document(
                client_id=self.client.id, module=3,
                doc_type="skill_matrix", path=str(pdf),
                created_at=date.today()
            ))
            s.commit()

        QMessageBox.information(self, "PDF creado",
                                f"Skill Matrix exportada: {pdf.name}")
        self.accept()
