'use client';

interface GirihPatternProps {
  opacity?: number;
  className?: string;
}

export function GirihPattern({ opacity = 0.05, className = '' }: GirihPatternProps) {
  return (
    <svg
      className={`absolute inset-0 w-full h-full ${className}`}
      style={{ opacity }}
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        <pattern
          id="girih-tile"
          x="0"
          y="0"
          width="100"
          height="100"
          patternUnits="userSpaceOnUse"
        >
          {/* 8-point girih star strapwork - tileable 100x100 module */}
          <line x1="50" y1="0" x2="50" y2="25" stroke="var(--color-naqsh-line)" strokeWidth="1.5" />
          <line x1="50" y1="75" x2="50" y2="100" stroke="var(--color-naqsh-line)" strokeWidth="1.5" />
          <line x1="0" y1="50" x2="25" y2="50" stroke="var(--color-naqsh-line)" strokeWidth="1.5" />
          <line x1="75" y1="50" x2="100" y2="50" stroke="var(--color-naqsh-line)" strokeWidth="1.5" />
          <line x1="12.5" y1="12.5" x2="37.5" y2="37.5" stroke="var(--color-naqsh-line)" strokeWidth="1.5" />
          <line x1="62.5" y1="62.5" x2="87.5" y2="87.5" stroke="var(--color-naqsh-line)" strokeWidth="1.5" />
          <line x1="87.5" y1="12.5" x2="62.5" y2="37.5" stroke="var(--color-naqsh-line)" strokeWidth="1.5" />
          <line x1="37.5" y1="62.5" x2="12.5" y2="87.5" stroke="var(--color-naqsh-line)" strokeWidth="1.5" />
          <line x1="50" y1="25" x2="37.5" y2="37.5" stroke="var(--color-naqsh-line)" strokeWidth="1.5" />
          <line x1="50" y1="25" x2="62.5" y2="37.5" stroke="var(--color-naqsh-line)" strokeWidth="1.5" />
          <line x1="50" y1="75" x2="37.5" y2="62.5" stroke="var(--color-naqsh-line)" strokeWidth="1.5" />
          <line x1="50" y1="75" x2="62.5" y2="62.5" stroke="var(--color-naqsh-line)" strokeWidth="1.5" />
          <line x1="25" y1="50" x2="37.5" y2="37.5" stroke="var(--color-naqsh-line)" strokeWidth="1.5" />
          <line x1="25" y1="50" x2="37.5" y2="62.5" stroke="var(--color-naqsh-line)" strokeWidth="1.5" />
          <line x1="75" y1="50" x2="62.5" y2="37.5" stroke="var(--color-naqsh-line)" strokeWidth="1.5" />
          <line x1="75" y1="50" x2="62.5" y2="62.5" stroke="var(--color-naqsh-line)" strokeWidth="1.5" />
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill="url(#girih-tile)" />
    </svg>
  );
}

export function GirihStar({ size = 24, className = '' }: { size?: number; className?: string }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      <line x1="50" y1="10" x2="50" y2="30" stroke="var(--color-naqsh-primary)" strokeWidth="3" />
      <line x1="50" y1="70" x2="50" y2="90" stroke="var(--color-naqsh-primary)" strokeWidth="3" />
      <line x1="10" y1="50" x2="30" y2="50" stroke="var(--color-naqsh-primary)" strokeWidth="3" />
      <line x1="70" y1="50" x2="90" y2="50" stroke="var(--color-naqsh-primary)" strokeWidth="3" />
      <line x1="20" y1="20" x2="35" y2="35" stroke="var(--color-naqsh-primary)" strokeWidth="3" />
      <line x1="65" y1="65" x2="80" y2="80" stroke="var(--color-naqsh-primary)" strokeWidth="3" />
      <line x1="80" y1="20" x2="65" y2="35" stroke="var(--color-naqsh-primary)" strokeWidth="3" />
      <line x1="35" y1="65" x2="20" y2="80" stroke="var(--color-naqsh-primary)" strokeWidth="3" />
    </svg>
  );
}

export function TamorLogo({ size = 40 }: { size?: number }) {
  return (
    <div className="flex items-center gap-3">
      <GirihStar size={size} />
      <div>
        <div className="text-xl font-bold text-[var(--primary)]">TaMoR</div>
      </div>
    </div>
  );
}
