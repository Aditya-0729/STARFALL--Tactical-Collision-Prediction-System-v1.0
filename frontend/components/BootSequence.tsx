"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";

const BOOT_LINES = [
  "STARFALL // TACTICAL COLLISION PREDICTION SYSTEM v1.0.0",
  "────────────────────────────────────────────────────────",
  "[OK] Initializing SGP4 orbital propagator...",
  "[OK] Connecting to PostgreSQL / TimescaleDB cluster...",
  "[OK] Loading TLE catalog — 18,431 tracked objects",
  "[OK] Synchronizing NASA NeoWs API — 847 NEO records",
  "[OK] Spawning AI prediction core (LSTM seq2seq)...",
  "[OK] WebSocket telemetry stream: ACTIVE",
  "[OK] Heliocentric coordinate solver: READY",
  "[WARN] 3 conjunction events within 72-hour window",
  "[CRIT] Object 2024-YR4 approach: T-minus 00:14:22",
  "────────────────────────────────────────────────────────",
  "SYSTEM NOMINAL. LAUNCHING HUD...",
];

interface Props {
  onComplete: () => void;
}

function getLineColor(line: string): string {
  if (typeof line !== "string") return "rgba(0,242,254,0.5)";
  if (line.includes("[CRIT]")) return "#ff0055";
  if (line.includes("[WARN]")) return "#ffb300";
  if (line.includes("[OK]")) return "#00f2fe";
  return "rgba(0,242,254,0.5)";
}

export default function BootSequence({ onComplete }: Props) {
  const [lines, setLines] = useState<string[]>([]);
  const [done, setDone] = useState(false);

  useEffect(() => {
    let i = 0;
    const interval = setInterval(() => {
      if (i < BOOT_LINES.length) {
        const nextLine = BOOT_LINES[i];
        if (nextLine !== undefined) {
          setLines((prev) => [...prev, nextLine]);
        }
        i++;
      } else {
        setDone(true);
        clearInterval(interval);
        setTimeout(onComplete, 1200);
      }
    }, 130);
    return () => clearInterval(interval);
  }, [onComplete]);

  return (
    <motion.div
      className="w-screen h-screen flex items-center justify-center"
      style={{ background: "#030305" }}
      exit={{ opacity: 0, scale: 1.04 }}
      transition={{ duration: 0.8 }}
    >
      <div className="font-mono text-xs leading-6 max-w-xl w-full px-8">
        {lines.map((line, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.12 }}
            style={{ color: getLineColor(line) }}
          >
            {line}
          </motion.div>
        ))}
        {done && (
          <span className="blink" style={{ color: "#00f2fe" }}>
            █
          </span>
        )}
      </div>
    </motion.div>
  );
}