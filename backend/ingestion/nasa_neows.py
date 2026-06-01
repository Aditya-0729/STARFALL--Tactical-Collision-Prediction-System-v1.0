"""
Ingests Near-Earth Object data from NASA's NeoWs API.
"""
import httpx
import logging
from datetime import datetime, timezone, date, timedelta
from app.config import settings

logger = logging.getLogger("starfall.ingestion.neows")

NEOWS_BASE = "https://api.nasa.gov/neo/rest/v1"


async def fetch_neos(days_ahead: int = 7) -> list[dict]:
    """Fetch NEO close approach data for the next N days."""
    start = date.today()
    end   = start + timedelta(days=days_ahead)

    url = f"{NEOWS_BASE}/feed"
    params = {
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "api_key": settings.nasa_api_key,
    }

    logger.info(f"Fetching NEOs from NASA NeoWs: {start} → {end}")

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

    neos = []
    for date_str, objects in data.get("near_earth_objects", {}).items():
        for obj in objects:
            approach = obj.get("close_approach_data", [{}])[0]
            diameter = obj.get("estimated_diameter", {}).get("meters", {})
            neos.append({
                "name": obj.get("name", "UNKNOWN"),
                "norad_id": f"NEO-{obj.get('id', 'UNKNOWN')}",
                "object_type": "NEO",
                "source": "NASA_NEOWS",
                "diameter_m": (
                    diameter.get("estimated_diameter_min", 0) +
                    diameter.get("estimated_diameter_max", 0)
                ) / 2,
                "close_approach_date": approach.get("close_approach_date_full"),
                "miss_distance_km": float(
                    approach.get("miss_distance", {}).get("kilometers", 0)
                ),
                "relative_velocity_km_s": float(
                    approach.get("relative_velocity", {}).get("kilometers_per_second", 0)
                ),
                "is_potentially_hazardous": obj.get("is_potentially_hazardous_asteroid", False),
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            })

    logger.info(f"Ingested {len(neos)} NEO records")
    return neos