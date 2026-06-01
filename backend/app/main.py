from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.routers import objects, telemetry, conjunctions, websocket
from app.db.database import engine, Base
from ingestion.scheduler import start_scheduler
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("starfall")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Start background ingestion scheduler
    scheduler = start_scheduler()
    logger.info("🚀 STARFALL backend online")
    yield
    scheduler.shutdown()
    logger.info("🛑 STARFALL backend shutting down")


app = FastAPI(
    title="Project STARFALL API",
    description="Real-time AI Collision Prediction & Space Debris Tracking",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(objects.router, prefix="/api/objects", tags=["Objects"])
app.include_router(telemetry.router, prefix="/api/telemetry", tags=["Telemetry"])
app.include_router(conjunctions.router, prefix="/api/conjunctions", tags=["Conjunctions"])
app.include_router(websocket.router, tags=["WebSocket"])


@app.get("/health")
async def health():
    return {"status": "nominal", "system": "STARFALL", "version": "1.0.0"}