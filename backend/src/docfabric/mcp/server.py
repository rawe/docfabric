from collections.abc import Callable
from uuid import UUID

from mcp.server.fastmcp import FastMCP

from docfabric.service.document import DocumentService


def create_mcp_server(get_service: Callable[[], DocumentService]) -> FastMCP:
    """Create an MCP server with read-only document tools.

    Args:
        get_service: Callable returning the DocumentService instance.
                     Called at tool invocation time (not at creation time).
    """
    mcp = FastMCP("DocFabric", stateless_http=True, json_response=True)
    mcp.settings.streamable_http_path = "/"

    @mcp.tool()
    async def list_documents(limit: int = 20, offset: int = 0) -> dict:
        """List documents with pagination.

        Args:
            limit: Maximum number of documents to return (default 20).
            offset: Number of documents to skip (default 0).
        """
        result = await get_service().list(limit=limit, offset=offset)
        return result.model_dump(mode="json")

    @mcp.tool()
    async def get_document(document_id: str) -> dict:
        """Get document metadata by ID.

        Args:
            document_id: UUID of the document.
        """
        result = await get_service().get(UUID(document_id))
        return result.model_dump(mode="json")

    @mcp.tool()
    async def read_document_content(
        document_id: str,
        offset: int | None = None,
        limit: int | None = None,
    ) -> str:
        """Read the markdown content of a document.

        Args:
            document_id: UUID of the document.
            offset: Character offset to start reading from.
            limit: Maximum number of characters to return.
        """
        result = await get_service().get_content(
            UUID(document_id), offset=offset, limit=limit
        )
        text = result.content
        if result.length < result.total_length:
            text += (
                f"\n\n---\n[offset={result.offset} length={result.length}"
                f" total={result.total_length}]"
            )
        return text

    return mcp
