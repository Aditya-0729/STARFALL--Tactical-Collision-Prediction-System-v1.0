"use client";

import dynamic from "next/dynamic";
import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import HUDLayout from "@/components/HUDLayout";
import BootSequence from "@/components/BootSequence";

// Disable SSR for 3D viewport (WebGL requires browser APIs)
const Viewport3D = dynamic(() => import("@/components/Viewport3D"), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center w-full h-full">
      <span className="text-cyan font-mono text-sm animate-pulse">
        INITIALIZING RENDER ENGINE...
      </span>
    </div>
  ),
});

export default function StarfallPage() {
  const [booted, setBooted] = useState(false);

  return (
    <AnimatePresence mode="wait">
      {!booted ? (
        <BootSequence key="boot" onComplete={() => setBooted(true)} />
      ) : (
        <motion.div
          key="hud"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1.2 }}
          className="w-screen h-screen overflow-hidden"
          style={{ background: "#030305" }}
        >
          <HUDLayout viewport={<Viewport3D />} />
        </motion.div>
      )}
    </AnimatePresence>
  );
}