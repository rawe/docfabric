from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine

from docfabric.conversion.converter import MarkdownConverter
from docfabric.db.repository import DocumentRepository
from docfabric.service.document import DocumentNotFoundError, DocumentService
from docfabric.storage import FileStorage


@pytest.fixture
def storage(tmp_path) -> FileStorage:
    return FileStorage(tmp_path)


@pytest.fixture
def converter() -> MarkdownConverter:
    from unittest.mock import MagicMock, patch

    with patch(
        "docfabric.conversion.converter.DocumentConverter"
    ) as mock_dc_class:
        mock_instance = MagicMock()
        mock_instance.convert.return_value.document.export_to_markdown.return_value = (
            "# Converted markdown"
        )
        mock_dc_class.return_value = mock_instance
        yield MarkdownConverter()


@pytest.fixture
def service(engine: AsyncEngine, storage: FileStorage, converter: MarkdownConverter):
    return DocumentService(
        repository=DocumentRepository(engine),
        storage=storage,
        converter=converter,
    )


class TestDocumentService:
    async def test_create(self, service: DocumentService):
        doc = await service.create(
            filename="test.pdf",
            content_type="application/pdf",
            data=b"pdf bytes",
            metadata={"author": "tester"},
        )
        assert doc.filename == "test.pdf"
        assert doc.content_type == "application/pdf"
        assert doc.size_bytes == 9
        assert doc.metadata == {"author": "tester"}

    async def test_get(self, service: DocumentService):
        created = await service.create(
            filename="test.pdf",
            content_type="application/pdf",
            data=b"pdf bytes",
        )
        fetched = await service.get(created.id)
        assert fetched.id == created.id
        assert fetched.filename == "test.pdf"

    async def test_get_not_found(self, service: DocumentService):
        with pytest.raises(DocumentNotFoundError):
            await service.get(uuid4())

    async def test_list(self, service: DocumentService):
        await service.create(
            filename="a.pdf",
            content_type="application/pdf",
            data=b"aaa",
        )
        await service.create(
            filename="b.pdf",
            content_type="application/pdf",
            data=b"bbb",
        )
        result = await service.list(limit=10, offset=0)
        assert result.total == 2
        assert len(result.items) == 2

    async def test_update(self, service: DocumentService):
        created = await service.create(
            filename="old.pdf",
            content_type="application/pdf",
            data=b"old data",
        )
        updated = await service.update(
            created.id,
            filename="new.pdf",
            content_type="application/pdf",
            data=b"new data here",
        )
        assert updated.filename == "new.pdf"
        assert updated.size_bytes == 13

    async def test_update_not_found(self, service: DocumentService):
        with pytest.raises(DocumentNotFoundError):
            await service.update(
                uuid4(),
                filename="x.pdf",
                content_type="application/pdf",
                data=b"x",
            )

    async def test_delete(self, service: DocumentService):
        created = await service.create(
            filename="del.pdf",
            content_type="application/pdf",
            data=b"to delete",
        )
        await service.delete(created.id)
        with pytest.raises(DocumentNotFoundError):
            await service.get(created.id)

    async def test_delete_not_found(self, service: DocumentService):
        with pytest.raises(DocumentNotFoundError):
            await service.delete(uuid4())

    async def test_get_content_full(self, service: DocumentService):
        created = await service.create(
            filename="content.pdf",
            content_type="application/pdf",
            data=b"pdf",
        )
        content = await service.get_content(created.id)
        assert content.content == "# Converted markdown"
        assert content.total_length == 20
        assert content.offset == 0
        assert content.length == 20

    async def test_get_content_with_offset_and_limit(self, service: DocumentService):
        created = await service.create(
            filename="content.pdf",
            content_type="application/pdf",
            data=b"pdf",
        )
        content = await service.get_content(created.id, offset=2, limit=5)
        assert content.content == "Conve"
        assert content.offset == 2
        assert content.length == 5
        assert content.total_length == 20

    async def test_create_cleans_up_on_conversion_failure(
        self, engine: AsyncEngine, storage: FileStorage
    ):
        from unittest.mock import MagicMock, patch

        with patch(
            "docfabric.conversion.converter.DocumentConverter"
        ) as mock_dc_class:
            mock_instance = MagicMock()
            mock_instance.convert.side_effect = RuntimeError("conversion failed")
            mock_dc_class.return_value = mock_instance
            bad_converter = MarkdownConverter()

        svc = DocumentService(
            repository=DocumentRepository(engine),
            storage=storage,
            converter=bad_converter,
        )

        with pytest.raises(RuntimeError, match="conversion failed"):
            await svc.create(
                filename="fail.pdf",
                content_type="application/pdf",
                data=b"bad pdf",
            )

        # Verify cleanup happened — no files left behind
        originals_dir = storage._base / "originals"
        if originals_dir.exists():
            remaining = list(originals_dir.iterdir())
            assert remaining == []
