from datetime import date
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QDoubleSpinBox, QSpinBox
)

from employ_toolkit.modules import kpi_panel
from employ_toolkit.core.models import Document
from employ_toolkit.core.storage import get_session


class KPIForm(QDialog):
    COLS = ["Indicador", "Actual", "Meta"]

    def __init__(self, client, parent=None):
        super().__init__(parent)
        self.client = client
        self.setWindowTitle(f"KPIs LinkedIn – {client.full_name}")
        self.resize(480, 380)

        lay = QVBoxLayout(self)

        self.table = QTableWidget(len(kpi_panel.INDICATORS), 3)
        self.table.setHorizontalHeaderLabels(self.COLS)

        for row, (name, unit) in enumerate(kpi_panel.INDICATORS):
            self.table.setItem(row, 0, QTableWidgetItem(name))

            if unit == "%":
                cur = QDoubleSpinBox(); cur.setRange(0, 100)
                meta = QDoubleSpinBox(); meta.setRange(0, 100)
            else:
                cur = QSpinBox();  cur.setRange(0, 999999)
                meta = QSpinBox(); meta.setRange(0, 999999)

            self.table.setCellWidget(row, 1, cur)
            self.table.setCellWidget(row, 2, meta)

        lay.addWidget(self.table)

        btn = QPushButton("Generar XLSX")
        btn.clicked.connect(self._generate)
        lay.addWidget(btn)

    # --------------------------------------------------
    def _generate(self):
        current = {}
        metas   = {}
        for row, (name, _) in enumerate(kpi_panel.INDICATORS):
            cur = self.table.cellWidget(row, 1).value()
            meta = self.table.cellWidget(row, 2).value()
            current[name] = cur
            metas[name] = meta

        xlsx = kpi_panel.generate_kpi_xlsx(self.client, current, metas)

        with get_session() as s:
            s.add(Document(
                client_id=self.client.id, module=1,
                doc_type="linkedin_kpis", path=str(xlsx),
                created_at=date.today()
            ))
            s.commit()

        QMessageBox.information(self, "XLSX creado", xlsx.name)
        self.accept()
