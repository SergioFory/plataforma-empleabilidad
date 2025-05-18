# gui/main.py
"""
Ventana Principal
-----------------
Muestra un menú lateral con los tres módulos y un botón para
crear un nuevo cliente (paso Intake).  Más adelante cada botón
cargará su respectiva pantalla; de momento sólo Intake funciona.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from employ_toolkit.modules import intake


class MainWindow(QMainWindow):
    def __init__(self, username: str, role: str):
        super().__init__()
        self.setWindowTitle("Plataforma de Empleabilidad")
        self.resize(800, 600)

        # ---------- Barra lateral ----------
        sidebar = QWidget()
        side_layout = QVBoxLayout(sidebar)

        lbl_user = QLabel(f"👤 {username} ({role})")
        lbl_user.setAlignment(Qt.AlignCenter)
        lbl_user.setFont(QFont("Arial", 10, QFont.Bold))

        btn_mod1 = QPushButton("Módulo 1 · Diagnóstico & Marca")
        btn_mod1.clicked.connect(self._not_implemented)

        btn_mod2 = QPushButton("Módulo 2 · Presencia Digital")
        btn_mod2.clicked.connect(self._not_implemented)

        btn_mod3 = QPushButton("Módulo 3 · Skills & Selección")
        btn_mod3.clicked.connect(self._not_implemented)

        btn_intake = QPushButton("➕ Nuevo Cliente (Intake)")
        btn_intake.clicked.connect(self._run_intake)

        # Añadir widgets al layout
        for w in (lbl_user, btn_mod1, btn_mod2, btn_mod3, btn_intake):
            side_layout.addWidget(w)
        side_layout.addStretch()

        # ---------- Área central (placeholder) ----------
        self.central_placeholder = QLabel(
            "Bienvenido.\nSelecciona una opción del menú.",
            alignment=Qt.AlignCenter,
        )
        self.central_placeholder.setFont(QFont("Arial", 12))

        # ---------- Layout principal ----------
        container = QWidget()
        main_layout = QHBoxLayout(container)
        main_layout.addWidget(sidebar, 1)
        main_layout.addWidget(self.central_placeholder, 4)

        self.setCentralWidget(container)

    # ------------------------------------------------------------------ #
    # Slots                                                               #
    # ------------------------------------------------------------------ #
    def _run_intake(self):
        """Lanza el wizard Intake en CLI (temporal)."""
        intake.intake_wizard({})
        self.central_placeholder.setText("Intake completado.\nRevisa la terminal.")

    def _not_implemented(self):
        self.central_placeholder.setText("📌 Esta sección se implementará\nen el próximo sprint.")


# ---------------------------------------------------------------------- #
# Ejecución directa (debug)                                              #
# ---------------------------------------------------------------------- #
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    win = MainWindow(username="demo", role="consultor")
    win.show()
    sys.exit(app.exec())
