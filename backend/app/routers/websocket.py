"""
WebSocket endpoint for real-time telemetry streaming.
Broadcasts live state vectors + AI prediction scores.
"""
import asyncio
import json
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.orbital_propagator import propagate_tle
from app.db.database import AsyncSessionLocal
from app.models.catalog import CatalogObject
from sqlalchemy import select
import os

router = APIRouter()
logger = logging.getLogger("starfall.ws")

active_connections: list[WebSocket] = []

# Load AI predictor if model exists
predictor = None
MODEL_PATH = "ml/checkpoints/orbital_lstm_best.pt"

def _load_predictor():
    global predictor
    try:
        from app.ml.lstm_predictor import TrajectoryPredictor
        if os.path.exists(MODEL_PATH):
            predictor = TrajectoryPredictor(model_path=MODEL_PATH)
            logger.info("✓ LSTM predictor loaded successfully")
        else:
            logger.info("No trained model found — running without AI predictions")
    except Exception as e:
        logger.warning(f"Could not load predictor: {e}")

_load_predictor()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    logger.info(f"WS client connected. Total: {len(active_connections)}")

    try:
        while True:
            payload = await build_live_payload()
            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        if websocket in active_connections:
            active_connections.remove(websocket)
        logger.info(f"WS client disconnected. Total: {len(active_connections)}")
    except Exception as e:
        logger.error(f"WS error: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)


async def build_live_payload() -> dict:
    now = datetime.now(timezone.utc)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(CatalogObject).where(
                CatalogObject.raw_tle1.isnot(None)
            ).limit(150)
        )
        objects = result.scalars().all()

    states = []
    for obj in objects:
        sv = propagate_tle(obj.raw_tle1, obj.raw_tle2, now)
        if not sv:
            continue

        # Base object data
        obj_data = {
            "id":           obj.id,
            "name":         obj.name,
            "norad_id":     obj.norad_id,
            "type":         obj.object_type,
            "x_km":         sv["x_km"],
            "y_km":         sv["y_km"],
            "z_km":         sv["z_km"],
            "vx_km_s":      sv["vx_km_s"],
            "vy_km_s":      sv["vy_km_s"],
            "vz_km_s":      sv["vz_km_s"],
            "altitude_km":  sv["altitude_km"],
            "speed_km_s":   sv["speed_km_s"],
            # Default AI values (shown when model not loaded)
            "anomaly_score": 0.0,
            "pc":            0.0,
            "risk_level":    "SAFE",
            "ai_active":     False,
        }

        # Run AI prediction if model is loaded
        if predictor is not None:
            try:
                from app.services.orbital_propagator import propagate_trajectory
                from datetime import timedelta

                # Get 4-hour history for this object
                history = propagate_trajectory(
                    obj.raw_tle1, obj.raw_tle2,
                    start=now - timedelta(hours=4),
                    hours=4,
                    step_minutes=5,
                )

                if len(history) >= 10:
                    result = predictor.predict(history, object_id=obj.id)
                    obj_data["anomaly_score"] = round(result.anomaly_score, 4)
                    obj_data["pc"]            = result.collision_probability
                    obj_data["risk_level"]    = result.risk_level
                    obj_data["ai_active"]     = True

                    # Include first 20 predicted positions for trail
                    obj_data["predicted_trail"] = result.predicted_trajectory[:20]

            except Exception as e:
                logger.debug(f"AI prediction failed for {obj.name}: {e}")

        states.append(obj_data)

    # Summary stats
    critical = sum(1 for s in states if s["risk_level"] == "CRITICAL")
    warning  = sum(1 for s in states if s["risk_level"] == "WARNING")
    ai_on    = any(s["ai_active"] for s in states)

    return {
        "ts":          now.isoformat(),
        "type":        "TELEMETRY",
        "count":       len(states),
        "objects":     states,
        "ai_active":   ai_on,
        "critical":    critical,
        "warning":     warning,
    }