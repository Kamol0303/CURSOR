import { cn } from "@/lib/cn";

const variants = {
  info: "bg-info-bg border-info/20 text-info",
  success: "bg-success-bg border-success/20 text-success",
  warning: "bg-warning-bg border-warning/20 text-warning",
  danger: "bg-danger-bg border-danger/20 text-danger",
} as const;

export function Alert({
  children,
  variant = "info",
  className,
}: {
  children: React.ReactNode;
  variant?: keyof typeof variants;
  className?: string;
}) {
  return (
    <div
      role="alert"
      className={cn(
        "rounded-lg border px-4 py-3 text-small",
        variants[variant],
        className,
      )}
    >
      {children}
    </div>
  );
}

export function Spinner({ className, label }: { className?: string; label?: string }) {
  return (
    <div className={cn("flex items-center justify-center gap-2", className)} role="status">
      <svg className="animate-spin h-5 w-5 text-naqsh-primary dark:text-naqsh-accent" viewBox="0 0 24 24" fill="none" aria-hidden>
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
      </svg>
      {label && <span className="text-small text-muted-foreground">{label}</span>}
    </div>
  );
}
