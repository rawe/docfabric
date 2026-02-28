import json
from uuid import UUID

from fastapi import APIRouter, Query, Request, Response, UploadFile
from fastapi import Form as FormField
from fastapi import HTTPException

from docfabric.service.document import DocumentService

router = APIRouter()


def get_document_service(request: Request) -> DocumentService:
    return request.app.state.document_service


@router.post("/documents", status_code=201)
async def create_document(
    request: Request,
    file: UploadFile,
    metadata: str | None = FormField(default=None),
):
    service = get_document_service(request)

    parsed_metadata = None
    if metadata is not None:
        try:
            parsed_metadata = json.loads(metadata)
        except (json.JSONDecodeError, TypeError):
            raise HTTPException(status_code=422, detail="Invalid metadata JSON")

    filename = file.filename or "unnamed"
    content_type = file.content_type or "application/octet-stream"
    data = await file.read()

    doc = await service.create(
        filename=filename,
        content_type=content_type,
        data=data,
        metadata=parsed_metadata,
    )
    return doc


@router.get("/documents")
async def list_documents(
    request: Request,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    service = get_document_service(request)
    return await service.list(limit=limit, offset=offset)


@router.get("/documents/{document_id}")
async def get_document(request: Request, document_id: UUID):
    service = get_document_service(request)
    return await service.get(document_id)


@router.put("/documents/{document_id}")
async def update_document(
    request: Request,
    document_id: UUID,
    file: UploadFile,
):
    service = get_document_service(request)

    filename = file.filename or "unnamed"
    content_type = file.content_type or "application/octet-stream"
    data = await file.read()

    return await service.update(
        document_id,
        filename=filename,
        content_type=content_type,
        data=data,
    )


@router.delete("/documents/{document_id}", status_code=204)
async def delete_document(request: Request, document_id: UUID):
    service = get_document_service(request)
    await service.delete(document_id)


@router.get("/documents/{document_id}/content")
async def get_document_content(
    request: Request,
    document_id: UUID,
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=1),
):
    service = get_document_service(request)
    return await service.get_content(document_id, offset=offset, limit=limit)


@router.get("/documents/{document_id}/original")
async def get_document_original(request: Request, document_id: UUID):
    service = get_document_service(request)
    meta = await service.get(document_id)
    data = service.get_original(document_id, meta.filename)
    return Response(
        content=data,
        media_type=meta.content_type,
        headers={"Content-Disposition": f'attachment; filename="{meta.filename}"'},
    )
