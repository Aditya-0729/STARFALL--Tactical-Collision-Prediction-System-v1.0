"use client";

import { Suspense, useRef, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Stars, Line } from "@react-three/drei";
import * as THREE from "three";
import { useOrbitalStore } from "@/lib/store";
import { useWebSocket } from "@/hooks/useWebSocket";

const EARTH_RADIUS_KM = 6371;
const SCALE = 1 / EARTH_RADIUS_KM;

// ─── Earth ────────────────────────────────────────────────────────────────────
function Earth() {
  const meshRef = useRef<THREE.Mesh>(null);
  useFrame((_, delta) => {
    if (meshRef.current) meshRef.current.rotation.y += delta * 0.05;
  });

  return (
    <group>
      <mesh ref={meshRef}>
        <sphereGeometry args={[1, 64, 64]} />
        <meshStandardMaterial
          color="#0a1628"
          emissive="#091420"
          roughness={0.8}
          metalness={0.1}
        />
      </mesh>
      <mesh>
        <sphereGeometry args={[1.002, 32, 32]} />
        <meshBasicMaterial
          color="#00f2fe"
          wireframe
          transparent
          opacity={0.07}
        />
      </mesh>
      <mesh>
        <sphereGeometry args={[1.06, 32, 32]} />
        <meshBasicMaterial
          color="#00f2fe"
          transparent
          opacity={0.04}
          side={THREE.BackSide}
        />
      </mesh>
    </group>
  );
}

// ─── Debris Cloud ─────────────────────────────────────────────────────────────
function DebrisCloud() {
  const objects = useOrbitalStore((s) => s.objects);

  // Always call hooks before any conditional return
  const { positions, colors, hasData } = useMemo(() => {
    const pos: number[] = [];
    const col: number[] = [];

    for (const obj of objects) {
      if (obj.x_km == null) continue;
      pos.push(obj.x_km * SCALE, obj.y_km * SCALE, obj.z_km * SCALE);
      if (obj.type === "NEO") {
        col.push(1.0, 0.70, 0.0);
      } else if (obj.type === "DEBRIS") {
        col.push(0.0, 0.95, 1.0);
      } else {
        col.push(0.6, 0.3, 1.0);
      }
    }

    return {
      positions: new Float32Array(pos),
      colors: new Float32Array(col),
      hasData: pos.length > 0,
    };
  }, [objects]);

  const geo = useMemo(() => {
    if (!hasData) return null;
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    g.setAttribute("color", new THREE.BufferAttribute(colors, 3));
    return g;
  }, [positions, colors, hasData]);

  if (!hasData || !geo) return null;

  return (
    <points geometry={geo}>
      <pointsMaterial
        size={0.02}
        vertexColors
        transparent
        opacity={0.9}
        sizeAttenuation
      />
    </points>
  );
}

// ─── Orbit Rings ──────────────────────────────────────────────────────────────
function OrbitRings() {
  const rings = [
    { r: 1.055, color: "#00f2fe", opacity: 0.12 },
    { r: 1.30,  color: "#00f2fe", opacity: 0.07 },
    { r: 6.61,  color: "#a78bfa", opacity: 0.10 },
  ];

  return (
    <>
      {rings.map((ring, idx) => {
        const pts: THREE.Vector3[] = [];
        for (let i = 0; i <= 128; i++) {
          const a = (i / 128) * Math.PI * 2;
          pts.push(
            new THREE.Vector3(
              Math.cos(a) * ring.r,
              0,
              Math.sin(a) * ring.r
            )
          );
        }
        return (
          <Line
            key={idx}
            points={pts}
            color={ring.color}
            lineWidth={0.5}
            transparent
            opacity={ring.opacity}
          />
        );
      })}
    </>
  );
}

// ─── Scene ────────────────────────────────────────────────────────────────────
function Scene() {
  useWebSocket();

  return (
    <>
      <ambientLight intensity={0.15} />
      <pointLight position={[10, 0, 0]} intensity={2} color="#fff5e0" />
      <Stars radius={120} depth={80} count={6000} factor={3} fade speed={0.3} />
      <Earth />
      <OrbitRings />
      <DebrisCloud />
      <OrbitControls
        enablePan={false}
        minDistance={1.5}
        maxDistance={20}
        zoomSpeed={0.7}
        rotateSpeed={0.5}
        autoRotate
        autoRotateSpeed={0.3}
      />
    </>
  );
}

// ─── Main Export ──────────────────────────────────────────────────────────────
export default function Viewport3D() {
  return (
    <Canvas
      camera={{ position: [0, 1.5, 4], fov: 55 }}
      gl={{ antialias: true, alpha: false }}
      style={{ background: "#030305" }}
    >
      <Suspense fallback={null}>
        <Scene />
      </Suspense>
    </Canvas>
  );
}