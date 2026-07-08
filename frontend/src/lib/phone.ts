/** Normalize user input to +998XXXXXXXXX (9 digits after country code). */
export function formatUzPhone(value: string): string {
  let digits = value.replace(/\D/g, "");
  if (digits.startsWith("998")) {
    digits = digits.slice(3);
  } else if (digits.startsWith("8") && digits.length > 9) {
    digits = digits.slice(1);
  }
  digits = digits.slice(0, 9);
  return `+998${digits}`;
}

export function isValidUzPhone(value: string): boolean {
  return /^\+998\d{9}$/.test(value);
}

/** Display-friendly mask: +998 90 123 45 67 */
export function displayUzPhone(value: string): string {
  const normalized = formatUzPhone(value);
  const digits = normalized.slice(4);
  if (digits.length === 0) return "+998";
  const parts = [digits.slice(0, 2), digits.slice(2, 5), digits.slice(5, 7), digits.slice(7, 9)].filter(Boolean);
  return `+998 ${parts.join(" ")}`.trim();
}
