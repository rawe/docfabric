from pathlib import Path

from docling.document_converter import DocumentConverter


class ConversionError(RuntimeError):
    pass


class MarkdownConverter:
    def __init__(self) -> None:
        self._converter = DocumentConverter()

    def convert(self, file_path: Path) -> str:
        try:
            result = self._converter.convert(str(file_path))
        except Exception as exc:
            raise ConversionError(str(exc)) from exc
        return result.document.export_to_markdown()
