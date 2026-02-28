from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///docfabric.db"
    storage_path: Path = Path("storage")

    model_config = {"env_file": ".env"}
