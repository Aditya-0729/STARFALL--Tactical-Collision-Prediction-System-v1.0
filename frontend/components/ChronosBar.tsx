"use client";

import { useTimeWarpStore } from "@/lib/store";

const MULTIPLIERS = [1, 10, 100, 1000] as const;

export default function ChronosBar() {
  const { multiplier, setMultiplier, timeOffset, setTimeOffset } =
    useTimeWarpStore();

  const simTime = new Date(Date.now() + timeOffset * 1000);

  return (
    <div
      className="h-full flex items-center font-mono"
      style={{
        borderTop: "1px solid rgba(0,242,254,0.15)",
        padding: "0 12px",
        gap: "12px",
        fontSize: "11px",
        background: "rgba(3,3,5,0.9)",
      }}
    >
      {/* Label */}
      <span
        style={{
          color: "#00f2fe",
          fontWeight: 700,
          letterSpacing: "0.12em",
          whiteSpace: "nowrap",
          textShadow: "0 0 8px rgba(0,242,254,0.5)",
        }}
      >
        ◈ CHRONOS
      </span>

      {/* Speed buttons */}
      <div className="flex" style={{ gap: "4px" }}>
        {MULTIPLIERS.map((m) => (
          <button
            key={m}
            onClick={() => setMultiplier(m)}
            style={{
              padding: "2px 8px",
              fontFamily: "monospace",
              fontSize: "10px",
              border: `1px solid ${
                multiplier === m
                  ? "#00f2fe"
                  : "rgba(0,242,254,0.2)"
              }`,
              color:
                multiplier === m
                  ? "#00f2fe"
                  : "rgba(0,242,254,0.4)",
              background:
                multiplier === m
                  ? "rgba(0,242,254,0.1)"
                  : "transparent",
              boxShadow:
                multiplier === m
                  ? "0 0 8px rgba(0,242,254,0.25)"
                  : "none",
              cursor: "pointer",
              whiteSpace: "nowrap",
            }}
          >
            {m}×
          </button>
        ))}
      </div>

      {/* Time offset label */}
      <span
        style={{ color: "rgba(0,242,254,0.4)", whiteSpace: "nowrap" }}
      >
        T+{Math.round(timeOffset / 3600)}H
      </span>

      {/* Scrubber */}
      <input
        type="range"
        min={0}
        max={72 * 3600}
        step={300}
        value={timeOffset}
        onChange={(e) => setTimeOffset(Number(e.target.value))}
        style={{ flex: 1, accentColor: "#00f2fe", minWidth: 0 }}
      />

      {/* +72H label */}
      <span
        style={{ color: "rgba(0,242,254,0.4)", whiteSpace: "nowrap" }}
      >
        +72H
      </span>

      {/* Sim timestamp */}
      <span
        style={{ color: "rgba(0,242,254,0.5)", whiteSpace: "nowrap" }}
      >
        {simTime.toUTCString().slice(4, 25)} UTC
      </span>

      {/* Reset */}
      <button
        onClick={() => {
          setTimeOffset(0);
          setMultiplier(1);
        }}
        style={{
          padding: "2px 8px",
          fontFamily: "monospace",
          fontSize: "10px",
          border: "1px solid rgba(0,242,254,0.2)",
          color: "rgba(0,242,254,0.5)",
          background: "transparent",
          cursor: "pointer",
          whiteSpace: "nowrap",
        }}
      >
        RESET
      </button>
    </div>
  );
}