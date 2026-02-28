import json
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4

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


async def _create_doc_with_markdown(
    service: DocumentService, markdown: str, filename="test.pdf"
) -> str:
    """Create a doc and overwrite its markdown content directly."""
    doc_id = await _create_doc(service, filename)
    service._storage.save_markdown(UUID(doc_id), markdown)
    return doc_id


class TestListTools:
    async def test_three_tools_registered(self, mcp_client: Client):
        tools = await mcp_client.list_tools()
        names = {t.name for t in tools}
        assert names == {
            "list_documents",
            "get_document_info",
            "read_document_content",
            "get_document_outline",
        }


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

    async def test_items_only_have_id_and_filename(
        self, mcp_client: Client, service
    ):
        await _create_doc(service, "a.pdf")
        result = await mcp_client.call_tool("list_documents", {})
        data = _parse_tool_result(result)
        item = data["items"][0]
        assert set(item.keys()) == {"id", "filename"}
        assert item["filename"] == "a.pdf"

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


class TestGetDocumentInfo:
    async def test_found(self, mcp_client: Client, service):
        doc_id = await _create_doc(service)
        result = await mcp_client.call_tool(
            "get_document_info", {"document_id": doc_id}
        )
        data = _parse_tool_result(result)
        assert data["id"] == doc_id
        assert data["filename"] == "test.pdf"
        assert data["content_type"] == "application/pdf"
        assert data["size_bytes"] == 9
        assert "created_at" in data
        assert "updated_at" in data

    async def test_not_found(self, mcp_client: Client):
        with pytest.raises(ToolError, match="not found"):
            await mcp_client.call_tool(
                "get_document_info", {"document_id": str(uuid4())}
            )


class TestReadDocumentContent:
    async def test_full_content(self, mcp_client: Client, service):
        doc_id = await _create_doc(service)
        result = await mcp_client.call_tool(
            "read_document_content", {"document_id": doc_id}
        )
        text = result.content[0].text
        assert text == "# Converted markdown"

    async def test_partial_content_includes_metadata_footer(
        self, mcp_client: Client, service
    ):
        doc_id = await _create_doc(service)
        result = await mcp_client.call_tool(
            "read_document_content",
            {"document_id": doc_id, "offset": 2, "limit": 5},
        )
        text = result.content[0].text
        assert text.startswith("Conve")
        assert "[offset=2 length=5 total=20]" in text

    async def test_full_content_has_no_metadata_footer(
        self, mcp_client: Client, service
    ):
        doc_id = await _create_doc(service)
        result = await mcp_client.call_tool(
            "read_document_content", {"document_id": doc_id}
        )
        text = result.content[0].text
        assert "---" not in text
        assert "[offset=" not in text

    async def test_not_found(self, mcp_client: Client):
        with pytest.raises(ToolError, match="not found"):
            await mcp_client.call_tool(
                "read_document_content", {"document_id": str(uuid4())}
            )


_OUTLINE_MD = """\
# Introduction
Intro text.
## Background
Background text.
### Details
Detail text.
## Methods
Methods text."""


class TestGetDocumentOutline:
    async def test_returns_sections_with_offset_and_length(
        self, mcp_client: Client, service
    ):
        doc_id = await _create_doc_with_markdown(service, _OUTLINE_MD)
        result = await mcp_client.call_tool(
            "get_document_outline", {"document_id": doc_id}
        )
        data = _parse_tool_result(result)
        sections = data["sections"]
        assert len(sections) == 4
        assert data["total_length"] == len(_OUTLINE_MD)

        # Check field names
        for s in sections:
            assert set(s.keys()) == {"level", "title", "offset", "length"}

        # Check titles and levels in order
        assert sections[0]["title"] == "Introduction"
        assert sections[0]["level"] == 1
        assert sections[1]["title"] == "Background"
        assert sections[1]["level"] == 2
        assert sections[2]["title"] == "Details"
        assert sections[2]["level"] == 3
        assert sections[3]["title"] == "Methods"
        assert sections[3]["level"] == 2

    async def test_h1_spans_entire_document(
        self, mcp_client: Client, service
    ):
        doc_id = await _create_doc_with_markdown(service, _OUTLINE_MD)
        result = await mcp_client.call_tool(
            "get_document_outline", {"document_id": doc_id}
        )
        data = _parse_tool_result(result)
        h1 = data["sections"][0]
        assert h1["offset"] == 0
        assert h1["length"] == len(_OUTLINE_MD)

    async def test_h2_includes_its_subheadings(
        self, mcp_client: Client, service
    ):
        doc_id = await _create_doc_with_markdown(service, _OUTLINE_MD)
        result = await mcp_client.call_tool(
            "get_document_outline", {"document_id": doc_id}
        )
        data = _parse_tool_result(result)
        bg = data["sections"][1]  # Background (H2)
        details = data["sections"][2]  # Details (H3)
        methods = data["sections"][3]  # Methods (H2)

        # Background section includes Details subsection
        assert bg["offset"] + bg["length"] == methods["offset"]
        # Details is contained within Background
        assert details["offset"] >= bg["offset"]
        assert details["offset"] + details["length"] <= bg["offset"] + bg["length"]

    async def test_offset_length_usable_with_read_tool(
        self, mcp_client: Client, service
    ):
        doc_id = await _create_doc_with_markdown(service, _OUTLINE_MD)
        outline = _parse_tool_result(
            await mcp_client.call_tool(
                "get_document_outline", {"document_id": doc_id}
            )
        )
        methods = outline["sections"][3]
        content = await mcp_client.call_tool(
            "read_document_content",
            {
                "document_id": doc_id,
                "offset": methods["offset"],
                "limit": methods["length"],
            },
        )
        text = content.content[0].text
        assert text.startswith("## Methods")
        assert "Methods text." in text

    async def test_no_headings(self, mcp_client: Client, service):
        doc_id = await _create_doc_with_markdown(service, "Just plain text.")
        result = await mcp_client.call_tool(
            "get_document_outline", {"document_id": doc_id}
        )
        data = _parse_tool_result(result)
        assert data["sections"] == []
        assert data["total_length"] == 16

    async def test_not_found(self, mcp_client: Client):
        with pytest.raises(ToolError, match="not found"):
            await mcp_client.call_tool(
                "get_document_outline", {"document_id": str(uuid4())}
            )
