from datetime import UTC, datetime
from uuid import uuid4

from docfabric.models.document import DocumentContent, DocumentList, DocumentMetadata


class TestDocumentMetadata:
    def test_roundtrip(self):
        now = datetime.now(UTC)
        doc = DocumentMetadata(
            id=uuid4(),
            filename="test.pdf",
            content_type="application/pdf",
            size_bytes=1024,
            metadata={"key": "value"},
            created_at=now,
            updated_at=now,
        )
        data = doc.model_dump(mode="json")
        restored = DocumentMetadata.model_validate(data)
        assert restored.filename == "test.pdf"
        assert restored.metadata == {"key": "value"}

    def test_from_dict(self):
        now = datetime.now(UTC)
        row = {
            "id": str(uuid4()),
            "filename": "report.docx",
            "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "size_bytes": 2048,
            "metadata": {},
            "created_at": now,
            "updated_at": now,
        }
        doc = DocumentMetadata.model_validate(row)
        assert doc.filename == "report.docx"
        assert doc.size_bytes == 2048


class TestDocumentList:
    def test_empty_list(self):
        dl = DocumentList(items=[], total=0, limit=20, offset=0)
        assert dl.total == 0
        assert dl.items == []


class TestDocumentContent:
    def test_content(self):
        dc = DocumentContent(
            content="# Hello",
            total_length=100,
            offset=0,
            length=7,
        )
        assert dc.content == "# Hello"
        assert dc.length == 7
