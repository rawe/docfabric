import shutil
from pathlib import Path
from uuid import UUID


class FileStorage:
    def __init__(self, base_path: Path) -> None:
        self._base = base_path

    def _original_dir(self, document_id: UUID) -> Path:
        return self._base / "originals" / str(document_id)

    def _markdown_path(self, document_id: UUID) -> Path:
        return self._base / "markdown" / f"{document_id}.md"

    def save_original(self, document_id: UUID, filename: str, data: bytes) -> Path:
        dir_ = self._original_dir(document_id)
        dir_.mkdir(parents=True, exist_ok=True)
        path = dir_ / filename
        path.write_bytes(data)
        return path

    def read_original(self, document_id: UUID, filename: str) -> bytes:
        return (self._original_dir(document_id) / filename).read_bytes()

    def original_path(self, document_id: UUID, filename: str) -> Path:
        return self._original_dir(document_id) / filename

    def save_markdown(self, document_id: UUID, content: str) -> Path:
        path = self._markdown_path(document_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def read_markdown(self, document_id: UUID) -> str:
        return self._markdown_path(document_id).read_text(encoding="utf-8")

    def delete(self, document_id: UUID) -> None:
        original_dir = self._original_dir(document_id)
        if original_dir.exists():
            shutil.rmtree(original_dir)
        md_path = self._markdown_path(document_id)
        if md_path.exists():
            md_path.unlink()
