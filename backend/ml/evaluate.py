"""
Evaluate the trained model on orbital trajectory prediction.

Usage (from backend/ folder with venv active):
    python -m ml.evaluate
"""
import numpy as np
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timezone, timedelta
from app.ml.lstm_predictor import TrajectoryPredictor
from app.services.orbital_propagator import propagate_trajectory
from app.config import settings


def evaluate():
    model_path = "ml/checkpoints/orbital_lstm_best.pt"

    if not os.path.exists(model_path):
        print("ERROR: No trained model found.")
        print("Run: python -m ml.train first")
        return

    print("Loading model...")
    predictor = TrajectoryPredictor(model_path=model_path)

    import psycopg2
    SYNC_DB_URL = settings.database_url.replace(
        "postgresql+asyncpg://", "postgresql://"
    )
    conn = psycopg2.connect(SYNC_DB_URL)
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, name, raw_tle1, raw_tle2
            FROM catalog
            WHERE raw_tle1 IS NOT NULL
            LIMIT 5
        """)
        rows = cur.fetchall()
    conn.close()

    if not rows:
        print("ERROR: No objects in database")
        return

    print(f"\nEvaluating on {len(rows)} objects...\n")
    print(f"{'─'*55}")
    print(f"  {'OBJECT':<20} {'MEAN ERR':>10} {'Pc':>12} {'RISK':<10}")
    print(f"{'─'*55}")

    all_errors = []

    for obj_id, name, tle1, tle2 in rows:
        now = datetime.now(timezone.utc)

        # 4-hour history
        history = propagate_trajectory(
            tle1, tle2,
            start=now - timedelta(hours=4),
            hours=4,
            step_minutes=5,
        )

        # 12-hour ground truth (matches model output_steps=144)
        truth = propagate_trajectory(
            tle1, tle2,
            start=now,
            hours=12,
            step_minutes=5,
        )

        if len(history) < 10 or len(truth) < 10:
            continue

        result = predictor.predict(history, object_id=obj_id)
        pred   = result.predicted_trajectory

        # Compare same length
        compare_len = min(len(pred), len(truth))
        errors = []
        for i in range(compare_len):
            dx = pred[i]["x_km"] - truth[i]["x_km"]
            dy = pred[i]["y_km"] - truth[i]["y_km"]
            dz = pred[i]["z_km"] - truth[i]["z_km"]
            errors.append((dx**2 + dy**2 + dz**2) ** 0.5)

        mean_err = np.mean(errors)
        all_errors.extend(errors)

        print(
            f"  {name[:20]:<20} "
            f"{mean_err:>8.1f} km "
            f"{result.collision_probability:>12.2e} "
            f"{result.risk_level:<10}"
        )

    print(f"{'─'*55}")
    if all_errors:
        print(f"  Overall mean error: {np.mean(all_errors):.1f} km")
        print(f"  Overall median:     {np.median(all_errors):.1f} km")
        print(f"{'─'*55}")

        mean = np.mean(all_errors)
        if mean < 500:
            print("  ✓ Excellent — model performing well")
        elif mean < 1500:
            print("  ~ Good — acceptable for presentation")
        elif mean < 3000:
            print("  ~ Fair — model needs more training data")
        else:
            print("  ✗ Poor — consider retraining with more data")

    print()


if __name__ == "__main__":
    evaluate()