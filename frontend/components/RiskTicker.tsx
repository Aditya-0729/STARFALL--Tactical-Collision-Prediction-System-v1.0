"use client";

import { useOrbitalStore } from "@/lib/store";
import { motion } from "framer-motion";

function riskColor(level?: string) {
  if (level === "CRITICAL") return "#ff0055";
  if (level === "WARNING")  return "#ffb300";
  return "#00f2fe";
}

export default function RiskTicker() {
  const objects  = useOrbitalStore((s) => s.objects);
  const aiActive = useOrbitalStore((s) => s.aiActive);

  // Derive risk events directly from objects
  const riskObjects = objects
    .filter((o) => o.risk_level === "CRITICAL" || o.risk_level === "WARNING")
    .sort((a, b) => {
      if (a.risk_level === "CRITICAL" && b.risk_level !== "CRITICAL") return -1;
      if (b.risk_level === "CRITICAL" && a.risk_level !== "CRITICAL") return 1;
      return (b.pc ?? 0) - (a.pc ?? 0);
    })
    .slice(0, 20);

  const criticalCount = objects.filter((o) => o.risk_level === "CRITICAL").length;
  const warningCount  = objects.filter((o) => o.risk_level === "WARNING").length;
  const safeCount     = objects.filter((o) => o.risk_level === "SAFE").length;

  return (
    <div className="h-full flex flex-col font-mono">

      {/* Header */}
      <div style={{
        padding: "6px 12px",
        borderBottom: "1px solid rgba(0,242,254,0.15)",
        color: "#ffb300",
        fontSize: "10px",
        fontWeight: 700,
        letterSpacing: "0.1em",
        textShadow: "0 0 8px rgba(255,179,0,0.5)",
      }}>
        ◈ RISK ASSESSMENT TICKER
      </div>

      {/* AI Status */}
      <div style={{
        padding: "4px 12px",
        borderBottom: "1px solid rgba(0,242,254,0.08)",
        fontSize: "9px",
        color: aiActive ? "#00f2fe" : "rgba(0,242,254,0.3)",
      }}>
        {aiActive ? "● AI PREDICTION ACTIVE" : "○ AI STANDBY — no model loaded"}
      </div>

      {/* Events list */}
      <div className="flex-1 overflow-y-auto">
        {!aiActive ? (
          <div style={{
            padding: "12px",
            fontSize: "10px",
            color: "rgba(0,242,254,0.3)",
            lineHeight: 1.6,
          }}>
            <div>AI MODEL NOT LOADED</div>
            <div style={{ marginTop: "4px", fontSize: "9px" }}>
              Restart backend to load trained model
            </div>
          </div>
        ) : riskObjects.length === 0 ? (
          <div style={{
            padding: "12px",
            fontSize: "10px",
            color: "rgba(0,242,254,0.3)",
            lineHeight: 1.6,
          }}>
            <div>NO ACTIVE EVENTS</div>
            <div style={{ marginTop: "4px", fontSize: "9px" }}>
              ALL OBJECTS WITHIN SAFE PARAMETERS
            </div>
          </div>
        ) : (
          riskObjects.map((obj, i) => (
            <motion.div
              key={obj.id}
              initial={{ opacity: 0, x: 16 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05 }}
              style={{
                padding: "8px 12px",
                borderBottom: "1px solid rgba(0,242,254,0.06)",
                borderLeft: `3px solid ${riskColor(obj.risk_level)}`,
                background: obj.risk_level === "CRITICAL"
                  ? "rgba(255,0,85,0.06)"
                  : "rgba(255,179,0,0.04)",
              }}
            >
              {/* Risk badge */}
              <div style={{
                fontSize: "9px",
                fontWeight: 700,
                letterSpacing: "0.1em",
                color: riskColor(obj.risk_level),
                textShadow: `0 0 6px ${riskColor(obj.risk_level)}80`,
                marginBottom: "3px",
              }}>
                [{obj.risk_level}]
              </div>

              {/* Object name */}
              <div style={{
                fontSize: "10px",
                color: "rgba(0,242,254,0.9)",
                marginBottom: "3px",
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
              }}>
                {obj.name}
              </div>

              {/* Metrics */}
              <div style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: "2px",
                fontSize: "9px",
                color: "rgba(0,242,254,0.5)",
              }}>
                <span>
                  Pc:{" "}
                  <span style={{ color: riskColor(obj.risk_level) }}>
                    {(obj.pc ?? 0).toExponential(2)}
                  </span>
                </span>
                <span>
                  ALT:{" "}
                  <span style={{ color: "#00f2fe" }}>
                    {obj.altitude_km != null
                      ? Math.round(obj.altitude_km) + " km"
                      : "—"}
                  </span>
                </span>
                <span>
                  Anom:{" "}
                  <span style={{ color: riskColor(obj.risk_level) }}>
                    {((obj.anomaly_score ?? 0) * 100).toFixed(1)}%
                  </span>
                </span>
                <span>
                  Spd:{" "}
                  <span style={{ color: "#00f2fe" }}>
                    {obj.speed_km_s != null
                      ? obj.speed_km_s.toFixed(1) + " km/s"
                      : "—"}
                  </span>
                </span>
              </div>
            </motion.div>
          ))
        )}
      </div>

      {/* Summary footer */}
      <div style={{
        borderTop: "1px solid rgba(0,242,254,0.1)",
        display: "grid",
        gridTemplateColumns: "1fr 1fr 1fr",
        textAlign: "center",
        padding: "6px 0",
      }}>
        {[
          { label: "SAFE",     count: safeCount,     color: "#00f2fe" },
          { label: "WARN",     count: warningCount,  color: "#ffb300" },
          { label: "CRIT",     count: criticalCount, color: "#ff0055" },
        ].map(({ label, count, color }) => (
          <div key={label}>
            <div style={{
              fontSize: "12px",
              fontWeight: 700,
              color,
              textShadow: count > 0 ? `0 0 6px ${color}80` : "none",
            }}>
              {count}
            </div>
            <div style={{
              fontSize: "8px",
              color: "rgba(0,242,254,0.3)",
              letterSpacing: "0.05em",
            }}>
              {label}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}