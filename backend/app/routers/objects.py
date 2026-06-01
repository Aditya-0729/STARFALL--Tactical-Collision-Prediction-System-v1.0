from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.database import get_db
from app.models.catalog import CatalogObject
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class ObjectOut(BaseModel):
    id: int
    norad_id: Optional[str]
    name: str
    object_type: Optional[str]
    diameter_m: Optional[float]
    source: Optional[str]

    class Config:
        from_attributes = True


@router.get("/", response_model=list[ObjectOut])
async def list_objects(
    object_type: Optional[str] = Query(None),
    limit: int = Query(100, le=1000),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    q = select(CatalogObject)
    if object_type:
        q = q.where(CatalogObject.object_type == object_type.upper())
    q = q.limit(limit).offset(offset)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/count")
async def count_objects(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CatalogObject.object_type, func.count().label("count"))
        .group_by(CatalogObject.object_type)
    )
    return {row.object_type or "UNKNOWN": row.count for row in result}


@router.get("/{object_id}", response_model=ObjectOut)
async def get_object(object_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CatalogObject).where(CatalogObject.id == object_id))
    obj = result.scalar_one_or_none()
    if not obj:
        from fastapi import HTTPException
        raise HTTPException(404, "Object not found")
    return obj