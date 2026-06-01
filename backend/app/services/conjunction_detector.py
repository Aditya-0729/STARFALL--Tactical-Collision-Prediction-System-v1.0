"""
Conjunction (close-approach) detection between tracked objects.
Uses pairwise minimum distance calculation over propagated trajectories.
"""
import math
import numpy as np
from datetime import datetime, timezone, timedelta
from app.services.orbital_propagator import propagate_tle


EARTH_RADIUS_KM = 6371.0
CONJUNCTION_THRESHOLD_KM = 10.0   # Flag events within 10 km
WARNING_PC_THRESHOLD   = 1e-4
CRITICAL_PC_THRESHOLD  = 1e-3


def compute_miss_distance(r1: dict, r2: dict) -> float:
    """Euclidean distance between two state vectors (km)."""
    return math.sqrt(
        (r1["x_km"] - r2["x_km"]) ** 2 +
        (r1["y_km"] - r2["y_km"]) ** 2 +
        (r1["z_km"] - r2["z_km"]) ** 2
    )


def foster_pc(miss_distance_km: float, combined_covariance_km: float = 0.2) -> float:
    """
    Simplified Foster-method Probability of Collision.
    For production use, replace with full Alfano or Chan 2D Pc.
    """
    ratio = miss_distance_km / combined_covariance_km
    # Gaussian approximation
    pc = math.exp(-0.5 * ratio**2) / (combined_covariance_km * math.sqrt(2 * math.pi))
    return min(pc, 1.0)


def classify_risk(pc: float) -> str:
    if pc >= CRITICAL_PC_THRESHOLD:
        return "CRITICAL"
    elif pc >= WARNING_PC_THRESHOLD:
        return "WARNING"
    return "SAFE"


def screen_conjunction(
    tle1_a: str, tle2_a: str,
    tle1_b: str, tle2_b: str,
    hours: float = 72,
    step_minutes: float = 2,
) -> dict | None:
    """
    Screen two objects for conjunction over the given time window.
    Returns the closest approach event or None if no conjunction found.
    """
    now = datetime.now(timezone.utc)
    best = None
    best_dist = float("inf")

    t = now
    steps = int((hours * 60) / step_minutes)

    for _ in range(steps):
        r_a = propagate_tle(tle1_a, tle2_a, t)
        r_b = propagate_tle(tle1_b, tle2_b, t)

        if r_a and r_b:
            dist = compute_miss_distance(r_a, r_b)
            if dist < best_dist:
                best_dist = dist
                best = {"tca": t.isoformat(), "miss_distance_km": dist}

        t += timedelta(minutes=step_minutes)

    if best and best_dist < CONJUNCTION_THRESHOLD_KM * 100:
        pc = foster_pc(best_dist)
        best["pc"] = pc
        best["risk_level"] = classify_risk(pc)
        return best

    return None