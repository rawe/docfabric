from contextlib import asynccontextmanager
from uuid import uuid4

import httpx
import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from httpx import ASGITransport

from docfabric.api.router import router
from docfabric.conversion.converter import MarkdownConverter
from docfabric.db.engine import create_engine, init_db
from docfabric.db.repository import DocumentRepository
from docfabric.service.document import DocumentNotFoundError, DocumentService
from docfabric.storage import FileStorage


@pytest.fixture
async def app(tmp_path):
    from unittest.mock import MagicMock, patch

    engine = create_engine("sqlite+aiosqlite://")
    await init_db(engine)

    storage = FileStorage(tmp_path)

    with patch("docfabric.conversion.converter.DocumentConverter") as mock_dc_class:
        mock_instance = MagicMock()
        mock_instance.convert.return_value.document.export_to_markdown.return_value = (
            "# Converted markdown"
        )
        mock_dc_class.return_value = mock_instance
        converter = MarkdownConverter()

    service = DocumentService(
        repository=DocumentRepository(engine),
        storage=storage,
        converter=converter,
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.document_service = service
        yield
        await engine.dispose()

    app = FastAPI(lifespan=lifespan)

    @app.exception_handler(DocumentNotFoundError)
    async def document_not_found_handler(
        request: Request, exc: DocumentNotFoundError
    ) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    app.include_router(router, prefix="/api")

    async with lifespan(app):
        yield app


@pytest.fixture
async def client(app: FastAPI):
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


def _upload(filename="test.pdf", content=b"pdf bytes", content_type="application/pdf"):
    return {"file": (filename, content, content_type)}


class TestHealth:
    async def test_health(self, client: httpx.AsyncClient):
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


class TestCreateDocument:
    async def test_create(self, client: httpx.AsyncClient):
        resp = await client.post("/api/documents", files=_upload())
        assert resp.status_code == 201
        body = resp.json()
        assert body["filename"] == "test.pdf"
        assert body["content_type"] == "application/pdf"
        assert body["size_bytes"] == 9
        assert "id" in body

    async def test_create_with_metadata(self, client: httpx.AsyncClient):
        resp = await client.post(
            "/api/documents",
            files=_upload(),
            data={"metadata": '{"author": "tester"}'},
        )
        assert resp.status_code == 201
        assert resp.json()["metadata"] == {"author": "tester"}

    async def test_create_invalid_metadata(self, client: httpx.AsyncClient):
        resp = await client.post(
            "/api/documents",
            files=_upload(),
            data={"metadata": "not json"},
        )
        assert resp.status_code == 422

    async def test_create_missing_file(self, client: httpx.AsyncClient):
        resp = await client.post("/api/documents")
        assert resp.status_code == 422


class TestListDocuments:
    async def test_empty(self, client: httpx.AsyncClient):
        resp = await client.get("/api/documents")
        assert resp.status_code == 200
        body = resp.json()
        assert body["items"] == []
        assert body["total"] == 0

    async def test_with_documents(self, client: httpx.AsyncClient):
        await client.post("/api/documents", files=_upload("a.pdf"))
        await client.post("/api/documents", files=_upload("b.pdf"))
        resp = await client.get("/api/documents")
        assert resp.status_code == 200
        assert resp.json()["total"] == 2
        assert len(resp.json()["items"]) == 2

    async def test_pagination(self, client: httpx.AsyncClient):
        await client.post("/api/documents", files=_upload("a.pdf"))
        await client.post("/api/documents", files=_upload("b.pdf"))
        await client.post("/api/documents", files=_upload("c.pdf"))

        resp = await client.get("/api/documents", params={"limit": 2, "offset": 0})
        body = resp.json()
        assert len(body["items"]) == 2
        assert body["total"] == 3

        resp = await client.get("/api/documents", params={"limit": 2, "offset": 2})
        body = resp.json()
        assert len(body["items"]) == 1
        assert body["total"] == 3


class TestGetDocument:
    async def test_found(self, client: httpx.AsyncClient):
        create_resp = await client.post("/api/documents", files=_upload())
        doc_id = create_resp.json()["id"]
        resp = await client.get(f"/api/documents/{doc_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == doc_id

    async def test_not_found(self, client: httpx.AsyncClient):
        resp = await client.get(f"/api/documents/{uuid4()}")
        assert resp.status_code == 404

    async def test_invalid_uuid(self, client: httpx.AsyncClient):
        resp = await client.get("/api/documents/not-a-uuid")
        assert resp.status_code == 422


class TestUpdateDocument:
    async def test_update(self, client: httpx.AsyncClient):
        create_resp = await client.post("/api/documents", files=_upload())
        doc_id = create_resp.json()["id"]

        resp = await client.put(
            f"/api/documents/{doc_id}",
            files=_upload("updated.pdf", b"new content"),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["filename"] == "updated.pdf"
        assert body["size_bytes"] == 11

    async def test_not_found(self, client: httpx.AsyncClient):
        resp = await client.put(
            f"/api/documents/{uuid4()}",
            files=_upload(),
        )
        assert resp.status_code == 404


class TestDeleteDocument:
    async def test_delete(self, client: httpx.AsyncClient):
        create_resp = await client.post("/api/documents", files=_upload())
        doc_id = create_resp.json()["id"]

        resp = await client.delete(f"/api/documents/{doc_id}")
        assert resp.status_code == 204
        assert resp.content == b""

        get_resp = await client.get(f"/api/documents/{doc_id}")
        assert get_resp.status_code == 404

    async def test_not_found(self, client: httpx.AsyncClient):
        resp = await client.delete(f"/api/documents/{uuid4()}")
        assert resp.status_code == 404


class TestGetDocumentContent:
    async def test_full_content(self, client: httpx.AsyncClient):
        create_resp = await client.post("/api/documents", files=_upload())
        doc_id = create_resp.json()["id"]

        resp = await client.get(f"/api/documents/{doc_id}/content")
        assert resp.status_code == 200
        body = resp.json()
        assert body["content"] == "# Converted markdown"
        assert body["total_length"] == 20
        assert body["offset"] == 0
        assert body["length"] == 20

    async def test_with_offset_and_limit(self, client: httpx.AsyncClient):
        create_resp = await client.post("/api/documents", files=_upload())
        doc_id = create_resp.json()["id"]

        resp = await client.get(
            f"/api/documents/{doc_id}/content",
            params={"offset": 2, "limit": 5},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["content"] == "Conve"
        assert body["offset"] == 2
        assert body["length"] == 5

    async def test_not_found(self, client: httpx.AsyncClient):
        resp = await client.get(f"/api/documents/{uuid4()}/content")
        assert resp.status_code == 404


class TestGetDocumentOriginal:
    async def test_original(self, client: httpx.AsyncClient):
        create_resp = await client.post("/api/documents", files=_upload())
        doc_id = create_resp.json()["id"]

        resp = await client.get(f"/api/documents/{doc_id}/original")
        assert resp.status_code == 200
        assert resp.content == b"pdf bytes"
        assert resp.headers["content-type"] == "application/pdf"
        assert "attachment" in resp.headers["content-disposition"]

    async def test_not_found(self, client: httpx.AsyncClient):
        resp = await client.get(f"/api/documents/{uuid4()}/original")
        assert resp.status_code == 404
