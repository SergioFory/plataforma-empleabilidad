# tests/test_gui_intake.py
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog
from sqlmodel import select

from employ_toolkit.core.models import Client
from employ_toolkit.core.storage import init_db, get_session
from employ_toolkit.gui.forms.intake_form import IntakeForm   # <- cambio aquí


def test_intake_saves(qtbot):
    init_db()

    form = IntakeForm()
    qtbot.addWidget(form)

    form.name.setText("QA User")
    form.email.setText("qa@test.com")
    form.phone.setText("123")
    form.profession.setText("Tester")
    form.age.setValue(28)
    form.disc.setCurrentText("I")

    qtbot.mouseClick(form.btn_save, Qt.LeftButton)
    assert form.result() == QDialog.Accepted

    with get_session() as s:
        assert s.exec(select(Client)
                      .where(Client.email == "qa@test.com")).first()
