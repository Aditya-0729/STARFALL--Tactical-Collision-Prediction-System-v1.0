"""
APScheduler-based background cron job orchestrator.
Uses synchronous psycopg2 connections to avoid event loop conflicts.
"""
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.config import settings
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime, timezone

logger = logging.getLogger("starfall.scheduler")

SYNC_DB_URL = settings.database_url.replace(
    "postgresql+asyncpg://", "postgresql://"
)

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}


def get_sync_connection():
    return psycopg2.connect(SYNC_DB_URL)


# ─── Job 1: Ingest TLEs from Space-Track (JSON format) ───────────────────────
def _ingest_tles():
    import requests
    logger.info("Starting TLE ingestion from Space-Track...")

    if not settings.spacetrack_user or not settings.spacetrack_pass:
        logger.warning("Space-Track credentials not set in .env, skipping")
        return

    base    = "https://www.space-track.org"
    session = requests.Session()
    session.headers.update(REQUEST_HEADERS)

    # Step 1: Login
    try:
        login = session.post(
            f"{base}/ajaxauth/login",
            data={
                "identity": settings.spacetrack_user,
                "password": settings.spacetrack_pass,
            },
            timeout=30,
        )
        login.raise_for_status()
        logger.info("Space-Track login successful")
    except Exception as e:
        logger.error(f"Space-Track login failed: {e}")
        return

    # Step 2: Fetch as JSON to get real NORAD IDs and proper names
    try:
        resp = session.get(
            f"{base}/basicspacedata/query/class/gp"
            f"/decay_date/null-val"
            f"/epoch/%3Enow-30"
            f"/orderby/norad_cat_id%20desc"
            f"/limit/500"
            f"/format/json",
            timeout=60,
        )
        resp.raise_for_status()
        logger.info(f"Space-Track returned {len(resp.text)} chars")
    except Exception as e:
        logger.error(f"Space-Track fetch failed: {e}")
        return
    finally:
        try:
            session.get(f"{base}/ajaxauth/logout", timeout=10)
        except Exception:
            pass

    # Step 3: Parse JSON
    try:
        data = resp.json()
    except Exception as e:
        logger.error(f"JSON parse failed: {e}")
        logger.debug(f"Raw preview: {resp.text[:300]}")
        return

    if not isinstance(data, list):
        logger.error(f"Unexpected response format: {type(data)}")
        logger.debug(f"Preview: {str(data)[:300]}")
        return

    logger.info(f"Parsed {len(data)} records from Space-Track JSON")

    # Step 4: Extract objects
    objects = []
    for item in data:
        try:
            norad_id = str(item.get("NORAD_CAT_ID", "")).strip()
            tle1     = item.get("TLE_LINE1", "").strip()
            tle2     = item.get("TLE_LINE2", "").strip()
            name     = item.get("OBJECT_NAME", f"OBJECT-{norad_id}").strip()
            obj_type = item.get("OBJECT_TYPE", "DEBRIS").strip()

            # Skip if missing essential fields
            if not norad_id or not tle1 or not tle2:
                continue

            # Skip if TLE lines are malformed
            if not tle1.startswith("1 ") or not tle2.startswith("2 "):
                continue

            # Map Space-Track object types to our types
            if obj_type == "PAYLOAD":
                db_type = "PAYLOAD"
            elif obj_type in ("ROCKET BODY", "DEBRIS"):
                db_type = "DEBRIS"
            else:
                db_type = "DEBRIS"

            objects.append((
                norad_id,
                name[:255],
                db_type,
                "SPACETRACK",
                tle1,
                tle2,
            ))

        except Exception:
            continue

    if not objects:
        logger.warning("No valid objects extracted from JSON")
        logger.debug(f"Sample record: {str(data[:1])}")
        return

    # Step 5: Insert into database
    conn = get_sync_connection()
    try:
        with conn.cursor() as cur:
            execute_values(cur, """
                INSERT INTO catalog
                    (norad_id, name, object_type, source, raw_tle1, raw_tle2)
                VALUES %s
                ON CONFLICT (norad_id) DO UPDATE SET
                    name       = EXCLUDED.name,
                    raw_tle1   = EXCLUDED.raw_tle1,
                    raw_tle2   = EXCLUDED.raw_tle2,
                    updated_at = NOW()
            """, objects)
        conn.commit()
        logger.info(f"TLE ingestion complete: {len(objects)} objects from Space-Track")
    except Exception as e:
        conn.rollback()
        logger.error(f"TLE DB insert failed: {e}")
    finally:
        conn.close()


# ─── Job 2: Ingest NEOs from NASA ────────────────────────────────────────────
def _ingest_neos():
    import requests
    from datetime import date, timedelta
    logger.info("Starting NEO ingestion...")

    start = date.today()
    end   = start + timedelta(days=7)

    try:
        resp = requests.get(
            "https://api.nasa.gov/neo/rest/v1/feed",
            params={
                "start_date": start.isoformat(),
                "end_date":   end.isoformat(),
                "api_key":    settings.nasa_api_key,
            },
            headers=REQUEST_HEADERS,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        logger.error(f"NEO fetch failed: {e}")
        return

    objects = []
    for date_str, items in data.get("near_earth_objects", {}).items():
        for obj in items:
            diameter     = obj.get("estimated_diameter", {}).get("meters", {})
            avg_diameter = (
                diameter.get("estimated_diameter_min", 0) +
                diameter.get("estimated_diameter_max", 0)
            ) / 2
            neo_id   = str(obj.get("id", "UNKNOWN"))[:40]
            norad_id = f"NEO-{neo_id}"
            name     = obj.get("name", "UNKNOWN NEO")[:255]
            objects.append((norad_id, name, "NEO", "NASA_NEOWS", avg_diameter))

    if not objects:
        logger.warning("No NEO objects found")
        return

    conn = get_sync_connection()
    try:
        with conn.cursor() as cur:
            execute_values(cur, """
                INSERT INTO catalog (norad_id, name, object_type, source, diameter_m)
                VALUES %s
                ON CONFLICT (norad_id) DO UPDATE SET
                    diameter_m = EXCLUDED.diameter_m,
                    updated_at = NOW()
            """, objects)
        conn.commit()
        logger.info(f"NEO ingestion complete: {len(objects)} objects")
    except Exception as e:
        conn.rollback()
        logger.error(f"NEO DB insert failed: {e}")
    finally:
        conn.close()


# ─── Job 3: Propagate Orbits ──────────────────────────────────────────────────
def _propagate_orbits():
    from app.services.orbital_propagator import propagate_tle
    logger.info("Propagating orbital states...")

    conn = get_sync_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, raw_tle1, raw_tle2
                FROM catalog
                WHERE raw_tle1 IS NOT NULL
                  AND raw_tle2 IS NOT NULL
                LIMIT 200
            """)
            objects = cur.fetchall()

        now    = datetime.now(timezone.utc)
        states = []

        for obj_id, tle1, tle2 in objects:
            sv = propagate_tle(tle1, tle2, now)
            if sv:
                states.append((
                    now,
                    obj_id,
                    sv["x_km"],
                    sv["y_km"],
                    sv["z_km"],
                    sv["vx_km_s"],
                    sv["vy_km_s"],
                    sv["vz_km_s"],
                    sv["altitude_km"],
                    "GEOCENTRIC",
                ))

        if states:
            with conn.cursor() as cur:
                execute_values(cur, """
                    INSERT INTO orbital_states
                        (time, object_id, x_km, y_km, z_km,
                         vx_km_s, vy_km_s, vz_km_s, altitude_km, coord_frame)
                    VALUES %s
                """, states)
            conn.commit()

        logger.info(f"Propagated {len(states)} orbital states")

    except Exception as e:
        conn.rollback()
        logger.error(f"Propagation failed: {e}")
    finally:
        conn.close()


# ─── Scheduler Setup ──────────────────────────────────────────────────────────
def start_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler()

    scheduler.add_job(
        _ingest_tles,
        IntervalTrigger(seconds=settings.tle_ingest_interval),
        id="ingest_tles",
        replace_existing=True,
        max_instances=1,
        next_run_time=datetime.now(),
    )
    scheduler.add_job(
        _ingest_neos,
        IntervalTrigger(seconds=settings.neo_ingest_interval),
        id="ingest_neos",
        replace_existing=True,
        max_instances=1,
        next_run_time=datetime.now(),
    )
    scheduler.add_job(
        _propagate_orbits,
        IntervalTrigger(seconds=settings.propagation_interval),
        id="propagate_orbits",
        replace_existing=True,
        max_instances=1,
        next_run_time=datetime.now(),
    )

    scheduler.start()
    logger.info("Scheduler started with 3 active jobs")
    return scheduler