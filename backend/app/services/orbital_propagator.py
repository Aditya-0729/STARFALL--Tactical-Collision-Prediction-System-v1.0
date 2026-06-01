"""
SGP4-based orbital propagator.
Converts TLE pairs to Cartesian state vectors (km, km/s) relative to Earth center.
"""
import math
from datetime import datetime, timezone
from sgp4.api import Satrec, jday
import numpy as np


def propagate_tle(tle1: str, tle2: str, epoch: datetime | None = None) -> dict | None:
    """
    Propagate a TLE to a given UTC epoch and return geocentric state vector.
    Returns None if propagation fails (decayed orbit, etc.).
    """
    if epoch is None:
        epoch = datetime.now(timezone.utc)

    sat = Satrec.twoline2rv(tle1, tle2)
    jd, fr = jday(
        epoch.year, epoch.month, epoch.day,
        epoch.hour, epoch.minute, epoch.second + epoch.microsecond / 1e6,
    )

    error_code, r, v = sat.sgp4(jd, fr)
    if error_code != 0:
        return None

    x, y, z = r          # km
    vx, vy, vz = v       # km/s
    altitude = math.sqrt(x**2 + y**2 + z**2) - 6371.0  # km above Earth surface

    return {
        "x_km": x, "y_km": y, "z_km": z,
        "vx_km_s": vx, "vy_km_s": vy, "vz_km_s": vz,
        "altitude_km": altitude,
        "speed_km_s": math.sqrt(vx**2 + vy**2 + vz**2),
        "epoch": epoch.isoformat(),
    }


def propagate_trajectory(
    tle1: str, tle2: str,
    start: datetime,
    hours: float = 72,
    step_minutes: float = 5,
) -> list[dict]:
    """Generate a series of state vectors over a time window."""
    from datetime import timedelta

    results = []
    t = start
    steps = int((hours * 60) / step_minutes)

    for _ in range(steps):
        state = propagate_tle(tle1, tle2, t)
        if state:
            results.append(state)
        t += timedelta(minutes=step_minutes)

    return results


def keplerian_to_cartesian(
    semi_major_axis_au: float,
    eccentricity: float,
    inclination_deg: float,
    raan_deg: float,
    arg_periapsis_deg: float,
    true_anomaly_deg: float,
) -> dict:
    """
    Convert Keplerian orbital elements to heliocentric Cartesian coordinates (AU).
    Used for planets and deep-space NEOs.
    """
    AU = 1.0  # Keep units in AU

    i   = math.radians(inclination_deg)
    raan = math.radians(raan_deg)
    w   = math.radians(arg_periapsis_deg)
    nu  = math.radians(true_anomaly_deg)

    a = semi_major_axis_au
    e = eccentricity
    r = a * (1 - e**2) / (1 + e * math.cos(nu))

    # Perifocal coords
    x_p = r * math.cos(nu)
    y_p = r * math.sin(nu)

    # Rotation matrices
    cos_raan, sin_raan = math.cos(raan), math.sin(raan)
    cos_i, sin_i       = math.cos(i),    math.sin(i)
    cos_w, sin_w       = math.cos(w),    math.sin(w)

    x = (cos_raan * cos_w - sin_raan * sin_w * cos_i) * x_p + \
        (-cos_raan * sin_w - sin_raan * cos_w * cos_i) * y_p
    y = (sin_raan * cos_w + cos_raan * sin_w * cos_i) * x_p + \
        (-sin_raan * sin_w + cos_raan * cos_w * cos_i) * y_p
    z = (sin_w * sin_i) * x_p + (cos_w * sin_i) * y_p

    return {"x_au": x, "y_au": y, "z_au": z, "r_au": r}