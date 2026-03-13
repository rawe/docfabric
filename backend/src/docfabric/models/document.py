from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class DocumentStatus(str, Enum):
    processing = "processing"
    ready = "ready"
    error = "error"


class DocumentMetadata(BaseModel):
    id: UUID
    filename: str
    content_type: str
    size_bytes: int
    status: DocumentStatus
    metadata: dict[str, str]
    error: str | None = None
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


class OutlineMode(str, Enum):
    flat = "flat"
    nested = "nested"


class OutlineSection(BaseModel):
    level: int
    title: str
    heading_path: str
    offset: int
    length: int


class DocumentOutline(BaseModel):
    sections: list[OutlineSection]
    total_length: int
