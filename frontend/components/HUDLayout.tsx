"use client";

import { ReactNode } from "react";
import TelemetryPanel from "./TelemetryPanel";
import RiskTicker from "./RiskTicker";
import ChronosBar from "./ChronosBar";
import StatusBar from "./StatusBar";

interface Props {
  viewport: ReactNode;
}

export default function HUDLayout({ viewport }: Props) {
  return (
    <div
      style={{
        width: "100vw",
        height: "100vh",
        display: "grid",
        gridTemplate: `
          "status  status  status" 32px
          "telem   view    risk"   1fr
          "chronos chronos chronos" 52px
          / 260px  1fr     260px
        `,
        gap: "1px",
        background: "rgba(0,242,254,0.06)",
        overflow: "hidden",
      }}
    >
      <div style={{ gridArea: "status", overflow: "hidden" }}>
        <StatusBar />
      </div>

      <div style={{
        gridArea: "telem",
        overflow: "hidden",
        background: "rgba(3,3,5,0.88)",
        borderRight: "1px solid rgba(0,242,254,0.12)",
      }}>
        <TelemetryPanel />
      </div>

      <div style={{
        gridArea: "view",
        background: "#030305",
        position: "relative",
        overflow: "hidden",
      }}>
        {viewport}
      </div>

      <div style={{
        gridArea: "risk",
        overflow: "hidden",
        background: "rgba(3,3,5,0.88)",
        borderLeft: "1px solid rgba(0,242,254,0.12)",
      }}>
        <RiskTicker />
      </div>

      <div style={{
        gridArea: "chronos",
        overflow: "hidden",
        background: "rgba(3,3,5,0.88)",
        borderTop: "1px solid rgba(0,242,254,0.12)",
      }}>
        <ChronosBar />
      </div>
    </div>
  );
}