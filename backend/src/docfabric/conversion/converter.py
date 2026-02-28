from pathlib import Path

from docling.document_converter import DocumentConverter


class MarkdownConverter:
    def __init__(self) -> None:
        self._converter = DocumentConverter()

    def convert(self, file_path: Path) -> str:
        result = self._converter.convert(str(file_path))
        return result.document.export_to_markdown()
