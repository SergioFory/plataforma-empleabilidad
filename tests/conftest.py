import pytest, sqlalchemy
from employ_toolkit.core import storage
from sqlmodel import create_engine

@pytest.fixture(autouse=True)
def _isolate_db(monkeypatch, tmp_path):
    # engine sólo para el test
    test_engine = create_engine("sqlite:///:memory:", echo=False)
    storage.SQLModel.metadata.create_all(test_engine)

    # parchea get_session para que use el engine temporal
    def _session():
        return sqlalchemy.orm.Session(test_engine, expire_on_commit=False)

    monkeypatch.setattr(storage, "get_session", _session)
    yield
