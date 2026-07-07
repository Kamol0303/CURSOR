"use client";

import { useEffect, useRef } from "react";

type TrailDot = { id: number; x: number; y: number };

export function MouseTrail({ color = "#c8932a" }: { color?: string }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const idRef = useRef(0);

  useEffect(() => {
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reducedMotion) return;

    let lastTime = 0;
    const throttleMs = 40;

    const onMove = (e: MouseEvent) => {
      const now = Date.now();
      if (now - lastTime < throttleMs) return;
      lastTime = now;

      const container = containerRef.current;
      if (!container) return;

      const dot = document.createElement("div");
      dot.className = "cyber-mouse-trail";
      dot.style.left = `${e.clientX - 5}px`;
      dot.style.top = `${e.clientY - 5}px`;
      dot.style.setProperty("--trail-color", color);
      container.appendChild(dot);

      window.setTimeout(() => dot.remove(), 1000);
    };

    window.addEventListener("mousemove", onMove, { passive: true });
    return () => window.removeEventListener("mousemove", onMove);
  }, [color]);

  return <div ref={containerRef} className="cyber-mouse-trail-layer" aria-hidden />;
}
