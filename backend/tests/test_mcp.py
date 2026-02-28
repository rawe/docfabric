import json
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from docfabric.conversion.converter import MarkdownConverter
from docfabric.db.engine import create_engine, init_db
from docfabric.db.repository import DocumentRepository
from docfabric.mcp.server import create_mcp_server
from docfabric.service.document import DocumentService
from docfabric.storage import FileStorage


def _parse_tool_result(result) -> dict:
    """Extract parsed JSON data from an MCP tool call result."""
    return json.loads(result.content[0].text)


@pytest.fixture
async def mcp_env(tmp_path):
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

    mcp = create_mcp_server(lambda: service)

    yield mcp, service

    await engine.dispose()


@pytest.fixture
async def mcp_client(mcp_env):
    mcp, _ = mcp_env
    async with Client(mcp) as client:
        yield client


@pytest.fixture
async def service(mcp_env):
    _, svc = mcp_env
    return svc


async def _create_doc(service: DocumentService, filename="test.pdf") -> str:
    doc = await service.create(
        filename=filename,
        content_type="application/pdf",
        data=b"pdf bytes",
    )
    return str(doc.id)


class TestListTools:
    async def test_three_tools_registered(self, mcp_client: Client):
        tools = await mcp_client.list_tools()
        names = {t.name for t in tools}
        assert names == {"list_documents", "get_document", "read_document_content"}


class TestListDocuments:
    async def test_empty(self, mcp_client: Client):
        result = await mcp_client.call_tool("list_documents", {})
        data = _parse_tool_result(result)
        assert data["items"] == []
        assert data["total"] == 0

    async def test_with_documents(self, mcp_client: Client, service):
        await _create_doc(service, "a.pdf")
        await _create_doc(service, "b.pdf")
        result = await mcp_client.call_tool("list_documents", {})
        data = _parse_tool_result(result)
        assert data["total"] == 2
        assert len(data["items"]) == 2

    async def test_pagination(self, mcp_client: Client, service):
        await _create_doc(service, "a.pdf")
        await _create_doc(service, "b.pdf")
        await _create_doc(service, "c.pdf")

        result = await mcp_client.call_tool(
            "list_documents", {"limit": 2, "offset": 0}
        )
        data = _parse_tool_result(result)
        assert len(data["items"]) == 2
        assert data["total"] == 3

        result = await mcp_client.call_tool(
            "list_documents", {"limit": 2, "offset": 2}
        )
        data = _parse_tool_result(result)
        assert len(data["items"]) == 1


class TestGetDocument:
    async def test_found(self, mcp_client: Client, service):
        doc_id = await _create_doc(service)
        result = await mcp_client.call_tool(
            "get_document", {"document_id": doc_id}
        )
        data = _parse_tool_result(result)
        assert data["id"] == doc_id
        assert data["filename"] == "test.pdf"

    async def test_not_found(self, mcp_client: Client):
        with pytest.raises(ToolError, match="not found"):
            await mcp_client.call_tool(
                "get_document", {"document_id": str(uuid4())}
            )


class TestReadDocumentContent:
    async def test_full_content(self, mcp_client: Client, service):
        doc_id = await _create_doc(service)
        result = await mcp_client.call_tool(
            "read_document_content", {"document_id": doc_id}
        )
        data = _parse_tool_result(result)
        assert data["content"] == "# Converted markdown"
        assert data["total_length"] == 20
        assert data["offset"] == 0
        assert data["length"] == 20

    async def test_with_offset_and_limit(self, mcp_client: Client, service):
        doc_id = await _create_doc(service)
        result = await mcp_client.call_tool(
            "read_document_content",
            {"document_id": doc_id, "offset": 2, "limit": 5},
        )
        data = _parse_tool_result(result)
        assert data["content"] == "Conve"
        assert data["offset"] == 2
        assert data["length"] == 5

    async def test_not_found(self, mcp_client: Client):
        with pytest.raises(ToolError, match="not found"):
            await mcp_client.call_tool(
                "read_document_content", {"document_id": str(uuid4())}
            )
