import { cn } from "@/lib/cn";
import type { ButtonHTMLAttributes } from "react";

const variants = {
  primary:
    "bg-naqsh-primary text-white shadow-sm hover:bg-[#163d32] active:scale-[0.98] dark:bg-naqsh-primary dark:hover:bg-[#1f5c4a]",
  secondary:
    "bg-surface text-foreground border border-border hover:bg-muted active:scale-[0.98] dark:bg-card dark:hover:bg-muted",
  outline:
    "border border-naqsh-primary/30 text-naqsh-primary hover:bg-naqsh-primary/5 active:scale-[0.98] dark:border-naqsh-accent/40 dark:text-naqsh-accent dark:hover:bg-naqsh-accent/10",
  ghost:
    "text-foreground-secondary hover:bg-muted hover:text-foreground active:scale-[0.98]",
  accent:
    "bg-naqsh-accent text-gray-900 shadow-sm hover:bg-[#b88425] active:scale-[0.98]",
  danger:
    "bg-danger text-white shadow-sm hover:bg-red-700 active:scale-[0.98]",
} as const;

const sizes = {
  sm: "h-8 px-3 text-small rounded-md gap-1.5",
  md: "h-10 px-4 text-body rounded-lg gap-2",
  lg: "h-11 px-5 text-body rounded-lg gap-2",
} as const;

type Variant = keyof typeof variants;
type Size = keyof typeof sizes;

export type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: Variant;
  size?: Size;
  loading?: boolean;
};

export function Button({
  className,
  variant = "primary",
  size = "md",
  loading,
  disabled,
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center font-medium transition-all duration-fast ease-out",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-naqsh-primary/30 focus-visible:ring-offset-2 focus-visible:ring-offset-background",
        "disabled:opacity-50 disabled:pointer-events-none disabled:active:scale-100",
        variants[variant],
        sizes[size],
        className,
      )}
      disabled={disabled || loading}
      {...props}
    >
      {loading && (
        <svg className="animate-spin h-4 w-4 shrink-0" viewBox="0 0 24 24" fill="none" aria-hidden>
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
      )}
      {children}
    </button>
  );
}
