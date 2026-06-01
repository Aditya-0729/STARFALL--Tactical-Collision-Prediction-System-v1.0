import { useEffect, useRef } from "react";
import { useOrbitalStore } from "@/lib/store";

const WS_URL         = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws";
const RECONNECT_DELAY = 3000;

export function useWebSocket() {
  const wsRef          = useRef<WebSocket | null>(null);
  const setObjects     = useOrbitalStore((s) => s.setObjects);
  const setWsConnected = useOrbitalStore((s) => s.setWsConnected);
  const setAiActive    = useOrbitalStore((s) => s.setAiActive);
  const setCritical    = useOrbitalStore((s) => s.setCriticalCount);
  const setWarning     = useOrbitalStore((s) => s.setWarningCount);

  useEffect(() => {
    let destroyed = false;

    function connect() {
      if (destroyed) return;
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        setWsConnected(true);
        console.log("[STARFALL] WebSocket connected");
      };

      ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.type === "TELEMETRY") {
            setObjects(payload.objects);
            setAiActive(payload.ai_active  ?? false);
            setCritical(payload.critical   ?? 0);
            setWarning(payload.warning     ?? 0);
          }
        } catch (e) {
          console.error("[STARFALL] WS parse error", e);
        }
      };

      ws.onerror = () => setWsConnected(false);

      ws.onclose = () => {
        setWsConnected(false);
        if (!destroyed) setTimeout(connect, RECONNECT_DELAY);
      };
    }

    connect();
    return () => {
      destroyed = true;
      wsRef.current?.close();
    };
  }, [setObjects, setWsConnected, setAiActive, setCritical, setWarning]);
}