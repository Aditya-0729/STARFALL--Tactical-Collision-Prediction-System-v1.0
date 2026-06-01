from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.database import get_db
from app.models.conjunction import Conjunction
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

router = APIRouter()


class ConjunctionOut(BaseModel):
    id: int
    primary_id: Optional[int]
    secondary_id: Optional[int]
    tca: datetime
    miss_distance_m: float
    pc: float
    risk_level: Optional[str]
    computed_at: Optional[datetime]

    class Config:
        from_attributes = True


@router.get("/active", response_model=list[ConjunctionOut])
async def active_conjunctions(
    min_pc: float = Query(1e-6, description="Minimum Pc threshold"),
    limit: int = Query(50, le=500),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Conjunction)
        .where(Conjunction.pc >= min_pc)
        .order_by(desc(Conjunction.pc))
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/critical", response_model=list[ConjunctionOut])
async def critical_conjunctions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Conjunction)
        .where(Conjunction.risk_level == "CRITICAL")
        .order_by(desc(Conjunction.pc))
        .limit(20)
    )
    return result.scalars().all()