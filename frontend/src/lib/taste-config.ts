/**
 * TMB taste-skill design read (trust-first government B2B dashboard).
 * Source: .agents/skills/design-taste-frontend + redesign-existing-projects
 *
 * Reading: public-sector education monitoring for administrators and teachers,
 * trust-first professional language, Forest palette (naqsh green + amber accent).
 */
export const TASTE_DIALS = {
  designVariance: 3,
  motionIntensity: 3,
  visualDensity: 5,
} as const;

/** Premium spring-like easing (not linear / ease-in-out). */
export const EASE_PREMIUM = "cubic-bezier(0.32, 0.72, 0, 1)";

/** Shape scale: inputs 12px, cards 16px, shells 20px, pills full. */
export const RADIUS = {
  input: "rounded-lg",
  card: "rounded-xl",
  shell: "rounded-2xl",
  pill: "rounded-full",
} as const;
