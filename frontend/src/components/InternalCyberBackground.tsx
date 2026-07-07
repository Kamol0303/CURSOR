"use client";

import { InteractiveCyberGrid } from "@/components/effects/InteractiveCyberGrid";
import { MatrixRain } from "@/components/effects/MatrixRain";
import { MouseTrail } from "@/components/effects/MouseTrail";

/**
 * Matrix rain, interactive grid, and mouse trail for authenticated internal pages.
 * Not used on login/auth screens — those use the Aeline-style AuthChrome landing shell.
 */
export function InternalCyberBackground() {
  return (
    <div className="internal-cyber-bg" aria-hidden>
      <MatrixRain color="#1b4d3e" opacity={0.1} />
      <div className="cyber-grid-static" />
      <InteractiveCyberGrid accentColor="#c8932a" />
      <MouseTrail color="#c8932a" />
    </div>
  );
}
