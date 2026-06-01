/**
 * Frontend orbital math utilities.
 * Mirror of backend propagator logic for client-side interpolation.
 */

export const EARTH_RADIUS_KM = 6371.0;
export const AU_TO_KM = 1.496e8;
export const THREE_SCALE = 1 / EARTH_RADIUS_KM; // 1 Three.js unit = 1 Earth radius

export function altitudeFromStateVector(x: number, y: number, z: number): number {
  return Math.sqrt(x * x + y * y + z * z) - EARTH_RADIUS_KM;
}

export function speedFromVelocity(vx: number, vy: number, vz: number): number {
  return Math.sqrt(vx * vx + vy * vy + vz * vz);
}

export function toThreeCoords(x_km: number, y_km: number, z_km: number) {
  return {
    x: x_km * THREE_SCALE,
    y: y_km * THREE_SCALE,
    z: z_km * THREE_SCALE,
  };
}

export function pcToHex(pc: number): string {
  if (pc >= 1e-3) return "#ff0055";   // CRITICAL
  if (pc >= 1e-4) return "#ffb300";   // WARNING
  return "#00f2fe";                    // SAFE
}

export function riskLabel(pc: number): string {
  if (pc >= 1e-3) return "CRITICAL";
  if (pc >= 1e-4) return "WARNING";
  return "SAFE";
}