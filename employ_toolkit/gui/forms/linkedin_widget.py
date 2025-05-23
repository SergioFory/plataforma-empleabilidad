# employ_toolkit/gui/forms/linkedin_widget.py
from PySide6.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QTextEdit,
    QPlainTextEdit, QTabWidget
)


class LinkedInWidget(QWidget):
    """Sub-formulario guiado para un perfil LinkedIn de alto nivel."""
    def __init__(self):
        super().__init__()

        layout = QFormLayout(self)

        # --- campos principales ------------------------------------
        self.headline = QLineEdit()
        self.headline.setMaxLength(120)

        self.about = QTextEdit()
        self.about.setFixedHeight(100)

        self.skills = QPlainTextEdit()
        self.skills.setPlaceholderText("Una skill por línea")

        self.exp = QTextEdit()
        self.exp.setPlaceholderText(
            "Cargo  |  Empresa  |  Fechas\n• Logro cuantificado 1\n• Logro 2…"
        )
        self.exp.setFixedHeight(120)

        self.banner = QLineEdit()
        self.banner.setPlaceholderText("URL o mensaje para banner")

        # --- pestañas extra ----------------------------------------
        tabs = QTabWidget()

        self.edu = QTextEdit()           # ✅  ahora existen
        self.cert = QTextEdit()
        self.lang = QTextEdit()

        tabs.addTab(self.edu,  "Educación")
        tabs.addTab(self.cert, "Certificaciones")
        tabs.addTab(self.lang, "Idiomas")

        # --- ensamblar ---------------------------------------------
        for lbl, w in (
            ("Headline (120 car.)", self.headline),
            ("About",               self.about),
            ("Skills",              self.skills),
            ("Experiencia",         self.exp),
            ("Banner URL / Texto",  self.banner),
        ):
            layout.addRow(lbl, w)

        layout.addRow(tabs)
