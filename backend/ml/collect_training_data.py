"""
Collects training data from orbital_states table.
Run this after the backend has been running for at least 1 hour.

Usage (from backend/ folder with venv active):
    python -m ml.collect_training_data
"""
import asyncio
import numpy as np
import os
import sys

# Make sure app modules are importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timezone, timedelta

OUTPUT_DIR = "ml/training_data"
MIN_POINTS = 10   # minimum state vectors per object to include
SEQ_LEN    = 48   # 48 steps of history (4 hours at 5-min intervals)
HORIZON    = 144  # 144 steps future (12 hours at 5-min intervals)


def collect():
    import psycopg2
    from app.config import settings
    from app.services.orbital_propagator import propagate_trajectory

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    SYNC_DB_URL = settings.database_url.replace(
        "postgresql+asyncpg://", "postgresql://"
    )

    conn = psycopg2.connect(SYNC_DB_URL)

    print("Fetching objects with TLE data...")
    with conn.cursor() as cur:
        cur.execute("""
            SELECT c.id, c.norad_id, c.name, c.raw_tle1, c.raw_tle2,
                   COUNT(o.time) as state_count
            FROM catalog c
            LEFT JOIN orbital_states o ON o.object_id = c.id
            WHERE c.raw_tle1 IS NOT NULL
              AND c.raw_tle2 IS NOT NULL
            GROUP BY c.id, c.norad_id, c.name, c.raw_tle1, c.raw_tle2
            HAVING COUNT(o.time) >= %s
            ORDER BY state_count DESC
        """, (MIN_POINTS,))
        objects = cur.fetchall()

    conn.close()

    print(f"Found {len(objects)} objects with enough history")

    if len(objects) == 0:
        print("ERROR: No objects found. Make sure the backend has been running")
        print("and orbital_states table has data.")
        return

    sequences_X = []
    sequences_Y = []
    generated   = 0

    for obj_id, norad_id, name, tle1, tle2, state_count in objects:
        # Generate 120-hour trajectory using SGP4
        now   = datetime.now(timezone.utc)
        start = now - timedelta(hours=48)

        traj = propagate_trajectory(
            tle1, tle2,
            start=start,
            hours=120,
            step_minutes=5,
        )

        if len(traj) < SEQ_LEN + HORIZON:
            continue

        # Sliding window — create multiple samples per object
        for start_idx in range(0, len(traj) - SEQ_LEN - HORIZON, 12):
            history = traj[start_idx: start_idx + SEQ_LEN]
            future  = traj[start_idx + SEQ_LEN: start_idx + SEQ_LEN + HORIZON]

            x_seq = np.array([[
                s["x_km"], s["y_km"], s["z_km"],
                s["vx_km_s"], s["vy_km_s"], s["vz_km_s"],
            ] for s in history], dtype=np.float32)

            y_seq = np.array([[
                s["x_km"], s["y_km"], s["z_km"],
            ] for s in future], dtype=np.float32)

            sequences_X.append(x_seq)
            sequences_Y.append(y_seq)
            generated += 1

        if generated % 200 == 0 and generated > 0:
            print(f"  Generated {generated} sequences so far...")

    if not sequences_X:
        print("ERROR: Could not generate any sequences.")
        return

    X = np.stack(sequences_X)
    Y = np.stack(sequences_Y)

    np.save(f"{OUTPUT_DIR}/X_train.npy", X)
    np.save(f"{OUTPUT_DIR}/Y_train.npy", Y)

    print(f"\nSaved {len(X)} training sequences to {OUTPUT_DIR}/")
    print(f"  X shape: {X.shape}  (samples, {SEQ_LEN} history steps, 6 features)")
    print(f"  Y shape: {Y.shape}  (samples, {HORIZON} future steps, 3 coords)")
    print(f"\nReady to train. Run: python -m ml.train")


if __name__ == "__main__":
    collect()