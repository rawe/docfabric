from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine

from docfabric.conversion.converter import MarkdownConverter
from docfabric.db.repository import DocumentRepository
from docfabric.models.document import OutlineMode
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


async def _create_doc_with_markdown(
    service: DocumentService, markdown: str
) -> UUID:
    doc = await service.create(
        filename="test.pdf",
        content_type="application/pdf",
        data=b"pdf bytes",
    )
    service._storage.save_markdown(doc.id, markdown)
    return doc.id


_OUTLINE_MD = """\
# Introduction
Intro text.
## Background
Background text.
### Details
Detail text.
## Methods
Methods text."""


class TestGetOutline:
    async def test_flat_default_returns_non_overlapping_sections(
        self, service: DocumentService
    ):
        doc_id = await _create_doc_with_markdown(service, _OUTLINE_MD)
        outline = await service.get_outline(doc_id)

        sections = outline.sections
        assert len(sections) == 4
        assert outline.total_length == len(_OUTLINE_MD)

        for s in sections:
            assert s.level > 0
            assert s.offset >= 0
            assert s.length > 0

    async def test_flat_sections_cover_full_document_without_overlap(
        self, service: DocumentService
    ):
        doc_id = await _create_doc_with_markdown(service, _OUTLINE_MD)
        outline = await service.get_outline(doc_id)

        sections = outline.sections
        # Each section starts where the previous one ends
        for i in range(1, len(sections)):
            prev_end = sections[i - 1].offset + sections[i - 1].length
            assert sections[i].offset == prev_end

        # First section starts at 0, last ends at total_length
        assert sections[0].offset == 0
        last = sections[-1]
        assert last.offset + last.length == outline.total_length

    async def test_flat_h1_only_covers_own_text(
        self, service: DocumentService
    ):
        doc_id = await _create_doc_with_markdown(service, _OUTLINE_MD)
        outline = await service.get_outline(doc_id)

        h1 = outline.sections[0]
        h2_bg = outline.sections[1]
        # H1 stops at H2
        assert h1.offset + h1.length == h2_bg.offset

    async def test_nested_h1_spans_entire_document(
        self, service: DocumentService
    ):
        doc_id = await _create_doc_with_markdown(service, _OUTLINE_MD)
        outline = await service.get_outline(doc_id, mode=OutlineMode.nested)

        h1 = outline.sections[0]
        assert h1.offset == 0
        assert h1.length == len(_OUTLINE_MD)

    async def test_nested_h2_includes_subheadings(
        self, service: DocumentService
    ):
        doc_id = await _create_doc_with_markdown(service, _OUTLINE_MD)
        outline = await service.get_outline(doc_id, mode=OutlineMode.nested)

        bg = outline.sections[1]  # Background (H2)
        details = outline.sections[2]  # Details (H3)
        methods = outline.sections[3]  # Methods (H2)

        # Background includes Details
        assert bg.offset + bg.length == methods.offset
        assert details.offset >= bg.offset
        assert details.offset + details.length <= bg.offset + bg.length

    async def test_no_headings(self, service: DocumentService):
        doc_id = await _create_doc_with_markdown(service, "Just plain text.")
        outline = await service.get_outline(doc_id)
        assert outline.sections == []
        assert outline.total_length == 16

    async def test_not_found(self, service: DocumentService):
        with pytest.raises(DocumentNotFoundError):
            await service.get_outline(uuid4())

    async def test_offset_length_retrieves_correct_content(
        self, service: DocumentService
    ):
        doc_id = await _create_doc_with_markdown(service, _OUTLINE_MD)
        outline = await service.get_outline(doc_id)

        methods = outline.sections[3]
        content = await service.get_content(
            doc_id, offset=methods.offset, limit=methods.length
        )
        assert content.content.startswith("## Methods")
        assert "Methods text." in content.content

    async def test_heading_with_no_body_still_returned(
        self, service: DocumentService
    ):
        md = "# Part One\n## Background\nSome text."
        doc_id = await _create_doc_with_markdown(service, md)
        outline = await service.get_outline(doc_id)

        assert len(outline.sections) == 2
        h1 = outline.sections[0]
        # H1 has only its heading line
        assert h1.title == "Part One"
        assert h1.length == len("# Part One\n")

    async def test_heading_path(self, service: DocumentService):
        doc_id = await _create_doc_with_markdown(service, _OUTLINE_MD)
        outline = await service.get_outline(doc_id)

        assert outline.sections[0].heading_path == "Introduction"
        assert outline.sections[1].heading_path == "Introduction > Background"
        assert outline.sections[2].heading_path == "Introduction > Background > Details"
        assert outline.sections[3].heading_path == "Introduction > Methods"
