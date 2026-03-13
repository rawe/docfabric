import asyncio
import re
from pathlib import Path
from uuid import UUID, uuid4

from docfabric.conversion.converter import MarkdownConverter
from docfabric.db.repository import DocumentRepository
from docfabric.models.document import (
    DocumentContent,
    DocumentList,
    DocumentMetadata,
    DocumentOutline,
    DocumentStatus,
    OutlineMode,
    OutlineSection,
)
from docfabric.storage import FileStorage

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

_NO_CONVERSION_TYPES = frozenset({"text/markdown", "text/x-markdown"})
_NO_CONVERSION_EXTENSIONS = frozenset({".md", ".markdown"})


class DocumentNotFoundError(Exception):
    def __init__(self, document_id: UUID) -> None:
        self.document_id = document_id
        super().__init__(f"Document {document_id} not found")


class DocumentNotReadyError(Exception):
    def __init__(self, document_id: UUID, status: str) -> None:
        self.document_id = document_id
        self.status = status
        super().__init__(f"Document {document_id} is not ready (status={status})")


def _row_to_metadata(row: dict) -> DocumentMetadata:
    return DocumentMetadata.model_validate(row)


def _needs_conversion(filename: str, content_type: str) -> bool:
    if content_type in _NO_CONVERSION_TYPES:
        return False
    if Path(filename).suffix.lower() in _NO_CONVERSION_EXTENSIONS:
        return False
    return True


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
        self._tasks: dict[UUID, asyncio.Task] = {}

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

        if _needs_conversion(filename, content_type):
            status = "processing"
        else:
            self._storage.save_markdown(doc_id, data.decode("utf-8"))
            status = "ready"

        row = await self._repo.insert(
            id=doc_id,
            filename=filename,
            content_type=content_type,
            size_bytes=len(data),
            metadata=meta,
            status=status,
        )

        if status == "processing":
            self._start_processing(doc_id, original_path)

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

        old_task = self._tasks.pop(document_id, None)
        if old_task and not old_task.done():
            old_task.cancel()

        self._storage.delete(document_id)
        original_path = self._storage.save_original(document_id, filename, data)

        if _needs_conversion(filename, content_type):
            status = "processing"
        else:
            self._storage.save_markdown(document_id, data.decode("utf-8"))
            status = "ready"

        row = await self._repo.update(
            document_id,
            filename=filename,
            content_type=content_type,
            size_bytes=len(data),
            status=status,
        )

        if status == "processing":
            self._start_processing(document_id, original_path)

        return _row_to_metadata(row)

    async def delete(self, document_id: UUID) -> None:
        old_task = self._tasks.pop(document_id, None)
        if old_task and not old_task.done():
            old_task.cancel()

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
        doc = await self.get(document_id)
        if doc.status != DocumentStatus.ready:
            raise DocumentNotReadyError(document_id, doc.status.value)

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
        doc = await self.get(document_id)
        if doc.status != DocumentStatus.ready:
            raise DocumentNotReadyError(document_id, doc.status.value)

        text = self._storage.read_markdown(document_id)
        total = len(text)

        headings = [
            (m.start(), len(m.group(1)), m.group(2).strip())
            for m in _HEADING_RE.finditer(text)
        ]

        sections = []
        path_stack: list[tuple[int, str]] = []
        for i, (start, level, title) in enumerate(headings):
            path_stack = [(l, t) for l, t in path_stack if l < level]
            path_stack.append((level, title))
            heading_path = " > ".join(t for _, t in path_stack)

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
                OutlineSection(
                    level=level, title=title, heading_path=heading_path,
                    offset=start, length=end - start,
                )
            )

        return DocumentOutline(sections=sections, total_length=total)

    def get_original(self, document_id: UUID, filename: str) -> bytes:
        return self._storage.read_original(document_id, filename)

    def _start_processing(self, doc_id: UUID, original_path: Path) -> None:
        old_task = self._tasks.pop(doc_id, None)
        if old_task and not old_task.done():
            old_task.cancel()
        task = asyncio.create_task(self._process_document(doc_id, original_path))
        self._tasks[doc_id] = task
        task.add_done_callback(lambda _: self._tasks.pop(doc_id, None))

    async def _process_document(self, doc_id: UUID, original_path: Path) -> None:
        try:
            markdown = await asyncio.to_thread(
                self._converter.convert, original_path
            )
            self._storage.save_markdown(doc_id, markdown)
            await self._repo.update_status(doc_id, status="ready")
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            await self._repo.update_status(
                doc_id, status="error", error=str(exc)
            )

    async def _wait_pending(self) -> None:
        tasks = list(self._tasks.values())
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
