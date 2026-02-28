from datetime import UTC, datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncEngine

from docfabric.db.tables import documents


class DocumentRepository:
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def insert(
        self,
        *,
        id: UUID,
        filename: str,
        content_type: str,
        size_bytes: int,
        metadata: dict[str, str],
    ) -> dict:
        now = datetime.now(UTC)
        values = {
            "id": str(id),
            "filename": filename,
            "content_type": content_type,
            "size_bytes": size_bytes,
            "metadata": metadata,
            "created_at": now,
            "updated_at": now,
        }
        async with self._engine.begin() as conn:
            await conn.execute(documents.insert().values(**values))
        return values

    async def get(self, id: UUID) -> dict | None:
        async with self._engine.connect() as conn:
            row = (
                await conn.execute(
                    documents.select().where(documents.c.id == str(id))
                )
            ).first()
        if row is None:
            return None
        return dict(row._mapping)

    async def list(self, *, limit: int = 20, offset: int = 0) -> tuple[list[dict], int]:
        async with self._engine.connect() as conn:
            total_row = await conn.execute(
                sa.select(sa.func.count()).select_from(documents)
            )
            total = total_row.scalar_one()

            rows = await conn.execute(
                documents.select()
                .order_by(documents.c.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            items = [dict(r._mapping) for r in rows]
        return items, total

    async def update(
        self,
        id: UUID,
        *,
        filename: str,
        content_type: str,
        size_bytes: int,
    ) -> dict | None:
        now = datetime.now(UTC)
        async with self._engine.begin() as conn:
            result = await conn.execute(
                documents.update()
                .where(documents.c.id == str(id))
                .values(
                    filename=filename,
                    content_type=content_type,
                    size_bytes=size_bytes,
                    updated_at=now,
                )
            )
            if result.rowcount == 0:
                return None
        return await self.get(id)

    async def delete(self, id: UUID) -> bool:
        async with self._engine.begin() as conn:
            result = await conn.execute(
                documents.delete().where(documents.c.id == str(id))
            )
        return result.rowcount > 0
