"use client";

import { useEffect, useState } from "react";
import { useOrbitalStore } from "@/lib/store";

export default function StatusBar() {
  const [time, setTime]  = useState("");
  const objectCount      = useOrbitalStore((s) => s.objects.length);
  const wsStatus         = useOrbitalStore((s) => s.wsConnected);
  const aiActive         = useOrbitalStore((s) => s.aiActive);
  const criticalCount    = useOrbitalStore((s) => s.criticalCount);
  const warningCount     = useOrbitalStore((s) => s.warningCount);

  useEffect(() => {
    const tick = () =>
      setTime(new Date().toUTCString().replace("GMT", "UTC"));
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, []);

  return (
    <div
      className="flex items-center justify-between px-3 h-full font-mono"
      style={{
        background: "rgba(3,3,5,0.95)",
        borderBottom: "1px solid rgba(0,242,254,0.2)",
        fontSize: "11px",
      }}
    >
      {/* Left */}
      <div className="flex items-center" style={{ gap: "12px" }}>
        <span style={{
          color: "#00f2fe",
          fontWeight: 700,
          letterSpacing: "0.12em",
          whiteSpace: "nowrap",
          textShadow: "0 0 8px rgba(0,242,254,0.6)",
        }}>
          ◈ PROJECT STARFALL
        </span>
        <span style={{ color: "rgba(0,242,254,0.4)", whiteSpace: "nowrap" }}>
          TACTICAL COLLISION PREDICTION SYSTEM v1.0
        </span>
      </div>

      {/* Right */}
      <div className="flex items-center" style={{ gap: "16px" }}>

        {/* AI Status */}
        <span style={{
          color: aiActive ? "#00f2fe" : "rgba(0,242,254,0.3)",
          whiteSpace: "nowrap",
          fontWeight: aiActive ? 700 : 400,
          textShadow: aiActive ? "0 0 8px rgba(0,242,254,0.5)" : "none",
        }}>
          ◈ AI {aiActive ? "ACTIVE" : "STANDBY"}
        </span>

        {/* Tracked count */}
        <span style={{ color: "rgba(0,242,254,0.6)", whiteSpace: "nowrap" }}>
          TRACKED:{" "}
          <span style={{ color: "#00f2fe", fontWeight: 700 }}>
            {objectCount}
          </span>
        </span>

        {/* Critical alerts */}
        {criticalCount > 0 && (
          <span style={{
            color: "#ff0055",
            whiteSpace: "nowrap",
            fontWeight: 700,
            textShadow: "0 0 8px rgba(255,0,85,0.6)",
            animation: "blink 1s step-end infinite",
          }}>
            ⚠ CRITICAL: {criticalCount}
          </span>
        )}

        {/* Warning alerts */}
        {warningCount > 0 && (
          <span style={{
            color: "#ffb300",
            whiteSpace: "nowrap",
            textShadow: "0 0 8px rgba(255,179,0,0.5)",
          }}>
            ⚠ WARNING: {warningCount}
          </span>
        )}

        {/* No alerts */}
        {criticalCount === 0 && warningCount === 0 && (
          <span style={{ color: "rgba(0,242,254,0.4)", whiteSpace: "nowrap" }}>
            ALL CLEAR
          </span>
        )}

        {/* WS Status */}
        <span className="flex items-center" style={{
          gap: "6px",
          color: wsStatus ? "#00f2fe" : "#ff0055",
          whiteSpace: "nowrap",
        }}>
          <span style={{
            display: "inline-block",
            width: "7px",
            height: "7px",
            borderRadius: "50%",
            background: wsStatus ? "#00f2fe" : "#ff0055",
            boxShadow: wsStatus ? "0 0 6px #00f2fe" : "0 0 6px #ff0055",
          }}/>
          {wsStatus ? "LIVE" : "OFFLINE"}
        </span>

        <span style={{ color: "rgba(0,242,254,0.35)", whiteSpace: "nowrap" }}>
          {time}
        </span>
      </div>
    </div>
  );
}