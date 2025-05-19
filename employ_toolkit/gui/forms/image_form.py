# employ_toolkit/gui/forms/image_form.py
from datetime import date
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QComboBox, QTextEdit,
    QPushButton, QMessageBox
)

from employ_toolkit.modules import image_guidelines
from employ_toolkit.core.models import Document
from employ_toolkit.core.storage import get_session


class ImageForm(QDialog):
    def __init__(self, client, parent=None):
        super().__init__(parent)
        self.client = client
        self.setWindowTitle(f"Imagen Profesional – {client.full_name}")
        self.resize(500, 550)

        lay = QFormLayout(self)

        # Vestimenta
        self.sector = QComboBox(); self.sector.addItems(["Formal", "Casual", "Creativo"])
        self.colores = QLineEdit(); self.colores.setPlaceholderText("Ej. Azul marino, gris...")
        self.accesorios = QLineEdit(); self.accesorios.setPlaceholderText("Reloj, pañuelo...")

        # Foto
        self.foto_res = QLineEdit("1080×1080 px")
        self.foto_plano = QComboBox(); self.foto_plano.addItems(["Primer plano", "Plano medio"])
        self.foto_fondo = QComboBox(); self.foto_fondo.addItems(["Neutro", "Brand"])
        self.foto_luz = QComboBox(); self.foto_luz.addItems(["Natural", "Suave difusa", "Estudio"])

        # Banner + consistencia
        self.banner = QTextEdit(); self.banner.setPlaceholderText("Mensaje visual del banner…")
        self.tipografia = QLineEdit("Open Sans")
        self.paleta = QLineEdit("#0B6FA4, #F4F4F4")
        self.logo = QComboBox(); self.logo.addItems(["Sí", "No"])

        # Añadir campos al layout
        lay.addRow("Sector", self.sector)
        lay.addRow("Colores recomendados", self.colores)
        lay.addRow("Accesorios permitidos", self.accesorios)

        lay.addRow("Resolución foto", self.foto_res)
        lay.addRow("Plano", self.foto_plano)
        lay.addRow("Fondo foto", self.foto_fondo)
        lay.addRow("Iluminación", self.foto_luz)

        lay.addRow("Mensaje banner LinkedIn", self.banner)
        lay.addRow("Tipografía", self.tipografia)
        lay.addRow("Paleta hex", self.paleta)
        lay.addRow("¿Logo personal?", self.logo)

        btn = QPushButton("Generar PDF")
        btn.clicked.connect(self._generate)
        lay.addRow(btn)

    # --------------------------------------------------
    def _generate(self):
        data = {
            "sector": self.sector.currentText(),
            "colores": self.colores.text(),
            "accesorios": self.accesorios.text(),
            "foto_res": self.foto_res.text(),
            "foto_plano": self.foto_plano.currentText(),
            "foto_fondo": self.foto_fondo.currentText(),
            "foto_luz": self.foto_luz.currentText(),
            "banner_msg": self.banner.toPlainText(),
            "tipografia": self.tipografia.text(),
            "paleta_hex": self.paleta.text(),
            "logo": self.logo.currentText(),
        }

        pdf_path = image_guidelines.generate_image_guidelines_pdf(self.client, data)

        with get_session() as s:
            s.add(Document(
                client_id=self.client.id, module=1,
                doc_type="image_guidelines", path=str(pdf_path),
                created_at=date.today()
            ))
            s.commit()

        QMessageBox.information(self, "PDF creado", pdf_path.name)
        self.accept()
