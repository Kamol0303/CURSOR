"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

const SQUARE_SIZE = 30;

type InteractiveCyberGridProps = {
  accentColor?: string;
};

export function InteractiveCyberGrid({ accentColor = "#c8932a" }: InteractiveCyberGridProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [dims, setDims] = useState({ cols: 0, rows: 0 });
  const [activeKey, setActiveKey] = useState<string | null>(null);
  const [rippleKeys, setRippleKeys] = useState<Set<string>>(new Set());

  const updateDims = useCallback(() => {
    setDims({
      cols: Math.ceil(window.innerWidth / SQUARE_SIZE),
      rows: Math.ceil(window.innerHeight / SQUARE_SIZE),
    });
  }, []);

  useEffect(() => {
    updateDims();
    window.addEventListener("resize", updateDims);
    return () => window.removeEventListener("resize", updateDims);
  }, [updateDims]);

  useEffect(() => {
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reducedMotion) return;

    const onMove = (e: MouseEvent) => {
      const col = Math.floor(e.clientX / SQUARE_SIZE);
      const row = Math.floor(e.clientY / SQUARE_SIZE);
      const key = `${row}-${col}`;
      setActiveKey(key);

      const nearby = new Set<string>();
      for (let r = row - 1; r <= row + 1; r++) {
        for (let c = col - 1; c <= col + 1; c++) {
          if (r !== row || c !== col) nearby.add(`${r}-${c}`);
        }
      }
      setRippleKeys(nearby);
    };

    window.addEventListener("mousemove", onMove, { passive: true });
    return () => window.removeEventListener("mousemove", onMove);
  }, []);

  const squares = useMemo(() => {
    const items: { key: string; row: number; col: number }[] = [];
    for (let row = 0; row < dims.rows; row++) {
      for (let col = 0; col < dims.cols; col++) {
        items.push({ key: `${row}-${col}`, row, col });
      }
    }
    return items;
  }, [dims]);

  return (
    <div
      ref={containerRef}
      className="cyber-interactive-grid"
      style={{ "--cyber-accent": accentColor } as React.CSSProperties}
      aria-hidden
    >
      {squares.map(({ key, row, col }) => (
        <div
          key={key}
          className={[
            "cyber-grid-square",
            activeKey === key ? "cyber-grid-square--active" : "",
            rippleKeys.has(key) ? "cyber-grid-square--ripple" : "",
          ]
            .filter(Boolean)
            .join(" ")}
          style={{
            left: col * SQUARE_SIZE,
            top: row * SQUARE_SIZE,
            width: SQUARE_SIZE,
            height: SQUARE_SIZE,
          }}
        />
      ))}
    </div>
  );
}
