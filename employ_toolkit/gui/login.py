# employ_toolkit/gui/login.py
"""
LoginWindow
===========

Ventana de inicio de sesión para la Plataforma de Empleabilidad.
Valida usuario y contraseña contra la tabla `users` (SQLite via SQLModel).

Usuarios demo (si corriste bootstrap.py):
    • admin     / admin123      (rol = admin)
    • consultor / consultor123  (rol = consultor)
"""

from PySide6.QtWidgets import (
    QWidget,
    QLineEdit,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QMessageBox,
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from sqlmodel import select
from passlib.hash import bcrypt

from employ_toolkit.core.storage import get_session
from employ_toolkit.core.models import User


class LoginWindow(QWidget):
    """Ventana básica de login."""

    def __init__(self) -> None:
        print(">>> Entrando a LoginWindow.__init__")
        super().__init__()

        self.setWindowTitle("Plataforma de Empleabilidad · Login")
        self.setFixedSize(320, 200)

        # ---------- Widgets ----------
        title = QLabel("Iniciar sesión", alignment=Qt.AlignCenter)
        title.setFont(QFont("Arial", 14, QFont.Bold))

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Usuario")

        self.pwd_input = QLineEdit()
        self.pwd_input.setPlaceholderText("Contraseña")
        self.pwd_input.setEchoMode(QLineEdit.Password)

        btn_login = QPushButton("Ingresar")
        btn_login.clicked.connect(self._handle_login)

        # ---------- Layout ----------
        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addSpacing(10)
        layout.addWidget(self.user_input)
        layout.addWidget(self.pwd_input)
        layout.addSpacing(10)
        layout.addWidget(btn_login)

        print(">>> LoginWindow construido OK")

    # ------------------------------------------------------------------ #
    # EVENTOS                                                            #
    # ------------------------------------------------------------------ #
    def _handle_login(self) -> None:
        """Verifica las credenciales."""
        username = self.user_input.text().strip()
        password = self.pwd_input.text()
        print(f">>> Intentando login con '{username}'")

        with get_session() as session:
            user: User | None = session.exec(
                select(User).where(User.username == username)
            ).first()

        if user and bcrypt.verify(password, user.password_hash):
            print(f">>> Login correcto: {user.username} ({user.role})")
            self._open_main_window(user)
        else:
            print(">>> Login fallido")
            QMessageBox.warning(self, "Error", "Credenciales inválidas")

    # ------------------------------------------------------------------ #
    # NAVEGACIÓN                                                         #
    # ------------------------------------------------------------------ #
    def _open_main_window(self, user: User) -> None:
        """Abre la ventana principal y cierra el login."""
        print(">>> Abriendo MainWindow…")
        # Import diferido para evitar ciclos
        from employ_toolkit.gui.main import MainWindow

        self.main = MainWindow(username=user.username, role=user.role)
        self.main.show()
        self.close()


# ---------------------------------------------------------------------- #
# EJECUCIÓN DIRECTA (debug)                                              #
# ---------------------------------------------------------------------- #
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    LoginWindow().show()
    sys.exit(app.exec())
