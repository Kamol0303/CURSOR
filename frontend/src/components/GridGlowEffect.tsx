"use client";

import { useMemo } from "react";
import { buildGridGlowShadow } from "@/lib/grid-glow-shadow";

type GridGlowEffectProps = {
  className?: string;
  columns?: number;
  rows?: number;
  color?: string;
  compact?: boolean;
};

export function GridGlowEffect({
  className = "",
  columns = 10,
  rows = 10,
  color = "#c8932a",
  compact = false,
}: GridGlowEffectProps) {
  const count = columns * rows;
  const shadow = useMemo(
    () => buildGridGlowShadow(compact ? 28 : 48, compact ? -2.8 : -4.8),
    [compact],
  );

  return (
    <div
      className={`grid-glow ${compact ? "grid-glow--compact" : ""} ${className}`}
      style={
        {
          "--grid-glow-color": color,
          "--grid-glow-shadow": shadow,
          gridTemplateColumns: `repeat(${columns}, 1fr)`,
          gridTemplateRows: `repeat(${rows}, 1fr)`,
        } as React.CSSProperties
      }
      aria-hidden
    >
      {Array.from({ length: count }, (_, i) => (
        <span key={i} className="grid-glow__tile" />
      ))}
    </div>
  );
}
