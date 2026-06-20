export function GirihBackground({opacity = 0.06}: {opacity?: number}) {
  return (
    <svg
      aria-hidden="true"
      className="absolute inset-0 h-full w-full"
      viewBox="0 0 100 100"
      preserveAspectRatio="none"
      style={{opacity}}
    >
      <defs>
        <pattern id="girih-tile" width="100" height="100" patternUnits="userSpaceOnUse">
          <path
            d="M50 6 L61 24 L82 18 L76 39 L94 50 L76 61 L82 82 L61 76 L50 94 L39 76 L18 82 L24 61 L6 50 L24 39 L18 18 L39 24 Z"
            fill="none"
            stroke="var(--color-naqsh-line)"
            strokeWidth="1.5"
          />
          <path
            d="M0 50 H18 M82 50 H100 M50 0 V18 M50 82 V100"
            fill="none"
            stroke="var(--color-naqsh-line)"
            strokeWidth="1.5"
          />
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill="url(#girih-tile)" />
    </svg>
  );
}
