"use client";

import { useOrbitalStore } from "@/lib/store";
import { motion } from "framer-motion";

function riskColor(risk?: string) {
  if (risk === "CRITICAL") return "#ff0055";
  if (risk === "WARNING")  return "#ffb300";
  return "#00f2fe";
}

function typeLabel(type?: string) {
  if (type === "NEO")    return { label: "NEO", color: "#ffb300" };
  if (type === "DEBRIS") return { label: "DEB", color: "#00f2fe" };
  if (type === "PLANET") return { label: "PLN", color: "#a78bfa" };
  return                        { label: "UNK", color: "rgba(0,242,254,0.4)" };
}

export default function TelemetryPanel() {
  const objects  = useOrbitalStore((s) => s.objects.slice(0, 80));
  const aiActive = useOrbitalStore((s) => s.aiActive);

  return (
    <div className="h-full flex flex-col" style={{ fontSize: "10px" }}>

      {/* Header */}
      <div className="px-3 py-1.5 font-mono font-bold tracking-widest"
        style={{
          borderBottom: "1px solid rgba(0,242,254,0.15)",
          color: "#00f2fe",
          textShadow: "0 0 8px rgba(0,242,254,0.5)",
          fontSize: "10px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <span>◈ LIVE VECTOR TELEMETRY</span>
        <span style={{
          fontSize: "9px",
          color: aiActive ? "#00f2fe" : "rgba(0,242,254,0.3)",
          fontWeight: aiActive ? 700 : 400,
        }}>
          {aiActive ? "AI ●" : "AI ○"}
        </span>
      </div>

      {/* Column headers */}
      <div className="font-mono px-2 py-1"
        style={{
          display: "grid",
          gridTemplateColumns: "24px 1fr 38px 42px 34px",
          color: "rgba(0,242,254,0.35)",
          borderBottom: "1px solid rgba(0,242,254,0.08)",
          fontSize: "9px",
          letterSpacing: "0.05em",
        }}
      >
        <span>TYP</span>
        <span>OBJECT</span>
        <span className="text-right">ALT</span>
        <span className="text-right">Pc</span>
        <span className="text-right">RISK</span>
      </div>

      {/* Rows */}
      <div className="flex-1 overflow-y-auto">
        {objects.length === 0 ? (
          <div className="p-3 font-mono animate-pulse"
            style={{ color: "rgba(0,242,254,0.3)", fontSize: "10px" }}>
            AWAITING TELEMETRY STREAM...
          </div>
        ) : (
          objects.map((obj, i) => {
            const badge = typeLabel(obj.type);
            const rc    = riskColor(obj.risk_level);
            const pc    = obj.pc ?? 0;

            return (
              <motion.div
                key={obj.id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: i * 0.003 }}
                className="font-mono"
                style={{
                  display: "grid",
                  gridTemplateColumns: "24px 1fr 38px 42px 34px",
                  fontSize: "10px",
                  borderBottom: "1px solid rgba(0,242,254,0.04)",
                  padding: "2px 8px",
                  alignItems: "center",
                  borderLeft: obj.risk_level === "CRITICAL"
                    ? "2px solid #ff0055"
                    : obj.risk_level === "WARNING"
                    ? "2px solid #ffb300"
                    : "2px solid transparent",
                  background: obj.risk_level === "CRITICAL"
                    ? "rgba(255,0,85,0.05)"
                    : obj.risk_level === "WARNING"
                    ? "rgba(255,179,0,0.04)"
                    : "transparent",
                }}
              >
                {/* Type */}
                <span style={{
                  color: badge.color,
                  fontSize: "8px",
                  fontWeight: 700,
                }}>
                  {badge.label}
                </span>

                {/* Name */}
                <span style={{
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                  paddingRight: "4px",
                  color: rc,
                }} title={obj.name}>
                  {obj.name?.slice(0, 12)}
                </span>

                {/* Altitude */}
                <span className="text-right tabular-nums"
                  style={{
                    color: obj.altitude_km != null && obj.altitude_km < 500
                      ? "#ffb300"
                      : "rgba(0,242,254,0.7)",
                  }}>
                  {obj.altitude_km != null ? Math.round(obj.altitude_km) : "—"}
                </span>

                {/* Pc value */}
                <span className="text-right tabular-nums"
                  style={{
                    color: pc > 1e-3 ? "#ff0055"
                         : pc > 1e-4 ? "#ffb300"
                         : "rgba(0,242,254,0.5)",
                    fontSize: "9px",
                  }}>
                  {aiActive && pc > 0 ? pc.toExponential(1) : "—"}
                </span>

                {/* Risk */}
                <span className="text-right"
                  style={{
                    color: rc,
                    fontSize: "8px",
                    fontWeight: 700,
                  }}>
                  {aiActive ? (obj.risk_level?.slice(0, 4) ?? "SAFE") : "—"}
                </span>
              </motion.div>
            );
          })
        )}
      </div>

      {/* Footer */}
      <div className="px-3 py-1 font-mono flex justify-between"
        style={{
          borderTop: "1px solid rgba(0,242,254,0.1)",
          color: "rgba(0,242,254,0.3)",
          fontSize: "9px",
        }}
      >
        <span>{objects.length} OBJECTS</span>
        <span>
          {objects.filter(o => o.risk_level === "CRITICAL").length} CRIT ·{" "}
          {objects.filter(o => o.risk_level === "WARNING").length} WARN
        </span>
      </div>
    </div>
  );
}