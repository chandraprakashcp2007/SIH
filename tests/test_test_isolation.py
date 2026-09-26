from pathlib import Path


def test_pytest_never_uses_operational_database():
    from backend.app.core.config import settings

    database_url = settings.DATABASE_URL.replace("\\", "/").lower()
    assert not database_url.endswith("/data/prahari.db")
    assert "test" in Path(database_url.rsplit("/", 1)[-1]).name
