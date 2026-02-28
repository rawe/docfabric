from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DocumentMetadata(BaseModel):
    id: UUID
    filename: str
    content_type: str
    size_bytes: int
    metadata: dict[str, str]
    created_at: datetime
    updated_at: datetime


class DocumentList(BaseModel):
    items: list[DocumentMetadata]
    total: int
    limit: int
    offset: int


class DocumentContent(BaseModel):
    content: str
    total_length: int
    offset: int
    length: int
