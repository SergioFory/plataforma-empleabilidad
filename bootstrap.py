"""
bootstrap.py
------------
Crea la base de datos y carga usuarios demo
(admin / consultor) si aún no existen.
"""

from sqlmodel import select
from passlib.hash import bcrypt
from employ_toolkit.core.storage import init_db, get_session
from employ_toolkit.core.models import User

def main() -> None:
    init_db()  # crea tablas si faltan

    with get_session() as session:
        # ¿Ya hay usuarios?
        if session.exec(select(User)).first():
            print("✓ Usuarios ya están cargados. Nada que hacer.")
            return

        demo_users = [
            User(username="admin",     password_hash=bcrypt.hash("admin123"),     role="admin"),
            User(username="consultor", password_hash=bcrypt.hash("consultor123"), role="consultor"),
        ]
        session.add_all(demo_users)
        session.commit()

    print("✓ Usuarios creados:\n  • admin / admin123\n  • consultor / consultor123")

if __name__ == "__main__":
    main()
