export function TmbLogo({ className = "w-12 h-12" }: { className?: string }) {
  return (
    <svg viewBox="0 0 48 48" className={className} aria-hidden="true">
      <path
        d="M24 4 L24 14 M24 34 L24 44 M4 24 L14 24 M34 24 L44 24 M24 14 L34 24 L24 34 L14 24 Z"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
      />
    </svg>
  );
}
