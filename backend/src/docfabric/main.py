from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.types import Receive, Scope, Send

from docfabric.api.router import router
from docfabric.config import Settings
from docfabric.conversion.converter import MarkdownConverter
from docfabric.db.engine import create_engine, init_db
from docfabric.db.repository import DocumentRepository
from docfabric.mcp.server import create_mcp_server
from docfabric.service.document import DocumentNotFoundError, DocumentService
from docfabric.storage import FileStorage


def _ensure_session_manager(mcp_instance) -> None:
    """Ensure a FastMCP instance has its session manager initialized."""
    if mcp_instance._session_manager is None:
        mcp_instance._session_manager = StreamableHTTPSessionManager(
            app=mcp_instance._mcp_server,
            event_store=mcp_instance._event_store,
            json_response=mcp_instance.settings.json_response,
            stateless=mcp_instance.settings.stateless_http,
        )


def create_app() -> FastAPI:
    settings = Settings()

    mcp = create_mcp_server(lambda: app.state.document_service)
    _ensure_session_manager(mcp)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        engine = create_engine(settings.database_url)
        await init_db(engine)
        repository = DocumentRepository(engine)
        storage = FileStorage(settings.storage_path)
        converter = MarkdownConverter()
        app.state.document_service = DocumentService(
            repository=repository, storage=storage, converter=converter
        )
        async with mcp.session_manager.run():
            yield
        await engine.dispose()

    app = FastAPI(lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    @app.exception_handler(DocumentNotFoundError)
    async def document_not_found_handler(
        request: Request, exc: DocumentNotFoundError
    ) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    app.include_router(router, prefix="/api")

    async def mcp_asgi_app(scope: Scope, receive: Receive, send: Send) -> None:
        await mcp.session_manager.handle_request(scope, receive, send)

    app.mount("/mcp", mcp_asgi_app)

    return app


app = create_app()
