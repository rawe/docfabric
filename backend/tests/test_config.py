from pathlib import Path

from docfabric.config import Settings


class TestSettings:
    def test_defaults(self):
        settings = Settings(
            _env_file=None,
        )
        assert settings.database_url == "sqlite+aiosqlite:///docfabric.db"
        assert settings.storage_path == Path("storage")

    def test_env_override(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///custom.db")
        monkeypatch.setenv("STORAGE_PATH", "/tmp/docs")
        settings = Settings(_env_file=None)
        assert settings.database_url == "sqlite+aiosqlite:///custom.db"
        assert settings.storage_path == Path("/tmp/docs")
