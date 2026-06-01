import { create } from "zustand";

export interface SpaceObject {
  id: number;
  name: string;
  norad_id?: string;
  type?: string;
  x_km: number;
  y_km: number;
  z_km: number;
  vx_km_s?: number;
  vy_km_s?: number;
  vz_km_s?: number;
  altitude_km?: number;
  speed_km_s?: number;
  anomaly_score?: number;
  pc?: number;
  risk_level?: string;
  ai_active?: boolean;
  predicted_trail?: Array<{x_km: number; y_km: number; z_km: number}>;
}

export interface ConjunctionEvent {
  id: number;
  primary_id?: number;
  secondary_id?: number;
  tca: string;
  miss_distance_m: number;
  pc: number;
  risk_level?: string;
}

interface OrbitalState {
  objects:        SpaceObject[];
  conjunctions:   ConjunctionEvent[];
  wsConnected:    boolean;
  aiActive:       boolean;
  criticalCount:  number;
  warningCount:   number;
  setObjects:         (objects: SpaceObject[]) => void;
  setConjunctions:    (conjunctions: ConjunctionEvent[]) => void;
  setWsConnected:     (connected: boolean) => void;
  setAiActive:        (active: boolean) => void;
  setCriticalCount:   (count: number) => void;
  setWarningCount:    (count: number) => void;
}

export const useOrbitalStore = create<OrbitalState>((set) => ({
  objects:       [],
  conjunctions:  [],
  wsConnected:   false,
  aiActive:      false,
  criticalCount: 0,
  warningCount:  0,
  setObjects:       (objects)       => set({ objects }),
  setConjunctions:  (conjunctions)  => set({ conjunctions }),
  setWsConnected:   (wsConnected)   => set({ wsConnected }),
  setAiActive:      (aiActive)      => set({ aiActive }),
  setCriticalCount: (criticalCount) => set({ criticalCount }),
  setWarningCount:  (warningCount)  => set({ warningCount }),
}));

interface TimeWarpState {
  multiplier:    1 | 10 | 100 | 1000;
  timeOffset:    number;
  setMultiplier: (m: 1 | 10 | 100 | 1000) => void;
  setTimeOffset: (t: number) => void;
}

export const useTimeWarpStore = create<TimeWarpState>((set) => ({
  multiplier:    1,
  timeOffset:    0,
  setMultiplier: (multiplier)  => set({ multiplier }),
  setTimeOffset: (timeOffset)  => set({ timeOffset }),
}));