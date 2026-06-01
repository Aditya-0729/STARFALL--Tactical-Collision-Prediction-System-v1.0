/**
 * STARFALL color palette and semantic mapping.
 */

export const COLORS = {
    obsidian:    "#030305",
    cyan:        "#00f2fe",
    amber:       "#ffb300",
    crimson:     "#ff0055",
    purple:      "#a78bfa",
    cyanDim:     "rgba(0,242,254,0.5)",
    cyanGhost:   "rgba(0,242,254,0.15)",
    panelBg:     "rgba(3,3,5,0.82)",
    glassBorder: "rgba(0,242,254,0.15)",
  } as const;
  
  export const OBJECT_TYPE_COLORS: Record<string, string> = {
    DEBRIS:  COLORS.cyan,
    NEO:     COLORS.amber,
    PLANET:  COLORS.purple,
    PAYLOAD: COLORS.cyanDim,
  };
  
  export const RISK_COLORS: Record<string, string> = {
    SAFE:     COLORS.cyan,
    WARNING:  COLORS.amber,
    CRITICAL: COLORS.crimson,
  };