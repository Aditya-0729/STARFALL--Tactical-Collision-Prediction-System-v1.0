"""
Ingests TLE/GP data from CelesTrak public feeds.
"""
import httpx
import logging
from datetime import datetime, timezone

logger = logging.getLogger("starfall.ingestion.celestrak")

TLE_FEEDS = {
    "debris":    "https://celestrak.org/SOCRATES/query.php?CATNR=25544&FORMAT=TLE",
    "stations":  "https://celestrak.org/pub/TLE/stations.txt",
    "leo":       "https://celestrak.org/pub/TLE/active.txt",
}


def parse_tle_lines(text: str) -> list[dict]:
    """Parse raw TLE text into structured dicts."""
    objects = []
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]

    i = 0
    while i + 2 < len(lines):
        name = lines[i]
        tle1 = lines[i + 1]
        tle2 = lines[i + 2]

        if tle1.startswith("1 ") and tle2.startswith("2 "):
            norad_id = tle1[2:7].strip()
            objects.append({
                "name": name,
                "norad_id": norad_id,
                "tle1": tle1,
                "tle2": tle2,
                "object_type": "DEBRIS",
                "source": "CELESTRAK",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            })
            i += 3
        else:
            i += 1

    return objects


async def fetch_active_tles(feed: str = "leo") -> list[dict]:
    """Fetch and parse TLEs from the given feed key."""
    url = TLE_FEEDS.get(feed, TLE_FEEDS["leo"])
    logger.info(f"Fetching TLEs from {url}")

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return parse_tle_lines(resp.text)