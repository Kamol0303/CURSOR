/** Box-shadow dots for grid-glow hover burst (ported from CodePen grid effect). */
export function buildGridGlowShadow(gapPx = 48, dotCoef = -4.8): string {
  const parts: string[] = ["0 0 0"];
  for (let i = 1; i <= 4; i++) {
    const g = i * gapPx;
    const c = i * dotCoef;
    parts.push(`${g}px 0 0 ${c}px`, `${-g}px 0 0 ${c}px`, `0 ${g}px 0 ${c}px`, `0 ${-g}px 0 ${c}px`);
    for (let j = 1; j <= 4; j++) {
      const d = i * j * 1.5 * dotCoef;
      const gj = j * gapPx;
      parts.push(
        `${g}px ${gj}px 0 ${d}px`,
        `${g}px ${-gj}px 0 ${d}px`,
        `${-g}px ${gj}px 0 ${d}px`,
        `${-g}px ${-gj}px 0 ${d}px`,
      );
    }
  }
  return parts.join(", ");
}
