from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.database import get_db
from app.models.orbital_state import OrbitalState
from app.models.catalog import CatalogObject
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

router = APIRouter()


class StateVectorOut(BaseModel):
    time: datetime
    object_id: int
    object_name: Optional[str]
    x_km: float
    y_km: float
    z_km: float
    vx_km_s: float
    vy_km_s: float
    vz_km_s: float
    altitude_km: Optional[float]

    class Config:
        from_attributes = True


@router.get("/latest", response_model=list[StateVectorOut])
async def latest_states(
    limit: int = Query(200, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """Return the most recent state vector per tracked object."""
    result = await db.execute(
        select(OrbitalState, CatalogObject.name)
        .join(CatalogObject, OrbitalState.object_id == CatalogObject.id)
        .order_by(desc(OrbitalState.time))
        .limit(limit)
    )
    rows = result.all()
    out = []
    for state, name in rows:
        d = StateVectorOut(
            time=state.time,
            object_id=state.object_id,
            object_name=name,
            x_km=state.x_km,
            y_km=state.y_km,
            z_km=state.z_km,
            vx_km_s=state.vx_km_s,
            vy_km_s=state.vy_km_s,
            vz_km_s=state.vz_km_s,
            altitude_km=state.altitude_km,
        )
        out.append(d)
    return out


@router.get("/{object_id}/history")
async def object_history(
    object_id: int,
    limit: int = Query(200, le=2000),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(OrbitalState)
        .where(OrbitalState.object_id == object_id)
        .order_by(desc(OrbitalState.time))
        .limit(limit)
    )
    return result.scalars().all()