from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QComboBox, QSpinBox,
    QPushButton, QMessageBox
)
from sqlmodel import select
from employ_toolkit.core.models import Client
from employ_toolkit.core.storage import get_session

DISC_TYPES = ["D", "I", "S", "C"]


class IntakeForm(QDialog):
    """Diálogo para registrar o actualizar un cliente."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nuevo Cliente – Intake")
        self.setFixedWidth(360)

        lay = QFormLayout(self)

        self.name = QLineEdit()
        self.email = QLineEdit()
        self.phone = QLineEdit()
        self.profession = QLineEdit()
        self.age = QSpinBox(); self.age.setRange(15, 90); self.age.setValue(30)
        self.disc = QComboBox(); self.disc.addItems(DISC_TYPES)

        lay.addRow("Nombre completo*", self.name)
        lay.addRow("Email*",           self.email)
        lay.addRow("Teléfono*",        self.phone)
        lay.addRow("Profesión*",       self.profession)
        lay.addRow("Edad*",            self.age)
        lay.addRow("Perfil DISC*",     self.disc)

        self.btn_save = QPushButton("Guardar")
        self.btn_save.setObjectName("btn_save")
        self.btn_save.clicked.connect(self.save)
        lay.addRow(self.btn_save)

    # ------------------------------------------------------------------ #
    def save(self):
        """Guarda o actualiza, y cierra el diálogo con Accepted."""
        if not all([self.name.text(), self.email.text(),
                    self.phone.text(), self.profession.text()]):
            QMessageBox.warning(self, "Faltan datos",
                                "Todos los campos son obligatorios.")
            return

        cliente = Client(
            full_name=self.name.text().strip(),
            email=self.email.text().strip(),
            phone=self.phone.text().strip(),
            profession=self.profession.text().strip(),
            age=int(self.age.value()),
            disc_type=self.disc.currentText(),
        )

        with get_session() as s:
            existing = s.exec(select(Client)
                              .where(Client.email == cliente.email)).first()

            if existing:
                # Actualizar registro existente
                cliente.id = existing.id
                s.merge(cliente)
            else:
                s.add(cliente)

            s.commit()

        self.accept()   # siempre Accepted al guardar correctamente
