# app.py
import sys, traceback
from PySide6.QtWidgets import QApplication

print(">>> Arrancando aplicación…")

try:
    print(">>> Importando LoginWindow…")
    from employ_toolkit.gui.login import LoginWindow
    
except Exception:
    print(">>> FALLO al importar LoginWindow:")
    traceback.print_exc()
    sys.exit(1)

try:
    app = QApplication(sys.argv)
    win = LoginWindow()
    win.show()
    print(">>> LoginWindow mostrado. Entrando al loop Qt.")
    sys.exit(app.exec())
except Exception:
    print(">>> Excepción en tiempo de ejecución:")
    traceback.print_exc()
    input("Pulsa Enter para cerrar…")
