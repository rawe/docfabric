from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncEngine

from docfabric.db.repository import DocumentRepository


class TestDocumentRepository:
    async def test_insert_and_get(self, engine: AsyncEngine):
        repo = DocumentRepository(engine)
        doc_id = uuid4()
        await repo.insert(
            id=doc_id,
            filename="test.pdf",
            content_type="application/pdf",
            size_bytes=1024,
            metadata={"author": "tester"},
        )
        row = await repo.get(doc_id)
        assert row is not None
        assert row["filename"] == "test.pdf"
        assert row["content_type"] == "application/pdf"
        assert row["size_bytes"] == 1024
        assert row["metadata"] == {"author": "tester"}

    async def test_get_nonexistent(self, engine: AsyncEngine):
        repo = DocumentRepository(engine)
        assert await repo.get(uuid4()) is None

    async def test_list_empty(self, engine: AsyncEngine):
        repo = DocumentRepository(engine)
        items, total = await repo.list()
        assert items == []
        assert total == 0

    async def test_list_with_pagination(self, engine: AsyncEngine):
        repo = DocumentRepository(engine)
        for i in range(5):
            await repo.insert(
                id=uuid4(),
                filename=f"doc{i}.pdf",
                content_type="application/pdf",
                size_bytes=100 * (i + 1),
                metadata={},
            )
        items, total = await repo.list(limit=2, offset=0)
        assert total == 5
        assert len(items) == 2

        items2, _ = await repo.list(limit=2, offset=2)
        assert len(items2) == 2

    async def test_update(self, engine: AsyncEngine):
        repo = DocumentRepository(engine)
        doc_id = uuid4()
        await repo.insert(
            id=doc_id,
            filename="old.pdf",
            content_type="application/pdf",
            size_bytes=100,
            metadata={},
        )
        updated = await repo.update(
            doc_id,
            filename="new.docx",
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            size_bytes=200,
        )
        assert updated is not None
        assert updated["filename"] == "new.docx"
        assert updated["size_bytes"] == 200

    async def test_update_nonexistent(self, engine: AsyncEngine):
        repo = DocumentRepository(engine)
        result = await repo.update(
            uuid4(),
            filename="x.pdf",
            content_type="application/pdf",
            size_bytes=1,
        )
        assert result is None

    async def test_delete(self, engine: AsyncEngine):
        repo = DocumentRepository(engine)
        doc_id = uuid4()
        await repo.insert(
            id=doc_id,
            filename="to_delete.pdf",
            content_type="application/pdf",
            size_bytes=50,
            metadata={},
        )
        assert await repo.delete(doc_id) is True
        assert await repo.get(doc_id) is None

    async def test_delete_nonexistent(self, engine: AsyncEngine):
        repo = DocumentRepository(engine)
        assert await repo.delete(uuid4()) is False
