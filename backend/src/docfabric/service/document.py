import re
from uuid import UUID, uuid4

from docfabric.conversion.converter import ConversionError, MarkdownConverter
from docfabric.db.repository import DocumentRepository
from docfabric.models.document import (
    DocumentContent,
    DocumentList,
    DocumentMetadata,
    DocumentOutline,
    OutlineMode,
    OutlineSection,
)
from docfabric.storage import FileStorage

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)


class DocumentNotFoundError(Exception):
    def __init__(self, document_id: UUID) -> None:
        self.document_id = document_id
        super().__init__(f"Document {document_id} not found")


def _row_to_metadata(row: dict) -> DocumentMetadata:
    return DocumentMetadata.model_validate(row)


class DocumentService:
    def __init__(
        self,
        repository: DocumentRepository,
        storage: FileStorage,
        converter: MarkdownConverter,
    ) -> None:
        self._repo = repository
        self._storage = storage
        self._converter = converter

    async def create(
        self,
        *,
        filename: str,
        content_type: str,
        data: bytes,
        metadata: dict[str, str] | None = None,
    ) -> DocumentMetadata:
        doc_id = uuid4()
        meta = metadata or {}

        original_path = self._storage.save_original(doc_id, filename, data)
        try:
            markdown = self._converter.convert(original_path)
        except ConversionError:
            self._storage.delete(doc_id)
            raise
        except Exception as exc:
            self._storage.delete(doc_id)
            raise ConversionError(str(exc)) from exc
        self._storage.save_markdown(doc_id, markdown)

        row = await self._repo.insert(
            id=doc_id,
            filename=filename,
            content_type=content_type,
            size_bytes=len(data),
            metadata=meta,
        )
        return _row_to_metadata(row)

    async def get(self, document_id: UUID) -> DocumentMetadata:
        row = await self._repo.get(document_id)
        if row is None:
            raise DocumentNotFoundError(document_id)
        return _row_to_metadata(row)

    async def list(self, *, limit: int = 20, offset: int = 0) -> DocumentList:
        items, total = await self._repo.list(limit=limit, offset=offset)
        return DocumentList(
            items=[_row_to_metadata(r) for r in items],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def update(
        self,
        document_id: UUID,
        *,
        filename: str,
        content_type: str,
        data: bytes,
    ) -> DocumentMetadata:
        existing = await self._repo.get(document_id)
        if existing is None:
            raise DocumentNotFoundError(document_id)

        self._storage.delete(document_id)
        original_path = self._storage.save_original(document_id, filename, data)
        try:
            markdown = self._converter.convert(original_path)
        except ConversionError:
            self._storage.delete(document_id)
            raise
        except Exception as exc:
            self._storage.delete(document_id)
            raise ConversionError(str(exc)) from exc
        self._storage.save_markdown(document_id, markdown)

        row = await self._repo.update(
            document_id,
            filename=filename,
            content_type=content_type,
            size_bytes=len(data),
        )
        return _row_to_metadata(row)

    async def delete(self, document_id: UUID) -> None:
        existed = await self._repo.delete(document_id)
        if not existed:
            raise DocumentNotFoundError(document_id)
        self._storage.delete(document_id)

    async def get_content(
        self,
        document_id: UUID,
        *,
        offset: int | None = None,
        limit: int | None = None,
    ) -> DocumentContent:
        await self.get(document_id)
        full = self._storage.read_markdown(document_id)
        total_length = len(full)

        start = offset or 0
        if limit is not None:
            end = start + limit
        else:
            end = total_length

        sliced = full[start:end]
        return DocumentContent(
            content=sliced,
            total_length=total_length,
            offset=start,
            length=len(sliced),
        )

    async def get_outline(
        self,
        document_id: UUID,
        *,
        mode: OutlineMode = OutlineMode.flat,
    ) -> DocumentOutline:
        await self.get(document_id)
        text = self._storage.read_markdown(document_id)
        total = len(text)

        headings = [
            (m.start(), len(m.group(1)), m.group(2).strip())
            for m in _HEADING_RE.finditer(text)
        ]

        sections = []
        for i, (start, level, title) in enumerate(headings):
            if mode is OutlineMode.nested:
                end = total
                for future_start, future_level, _ in headings[i + 1 :]:
                    if future_level <= level:
                        end = future_start
                        break
            else:
                if i + 1 < len(headings):
                    end = headings[i + 1][0]
                else:
                    end = total
            sections.append(
                OutlineSection(level=level, title=title, offset=start, length=end - start)
            )

        return DocumentOutline(sections=sections, total_length=total)

    def get_original(self, document_id: UUID, filename: str) -> bytes:
        return self._storage.read_original(document_id, filename)
