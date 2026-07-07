import { cn } from "@/lib/cn";

const variants = {
  default: "bg-muted text-foreground-secondary",
  primary: "bg-naqsh-primary/10 text-naqsh-primary dark:bg-naqsh-accent/15 dark:text-naqsh-accent",
  accent: "bg-naqsh-accent/15 text-[#8a6a1e] dark:text-naqsh-accent",
  success: "bg-success-bg text-success",
  warning: "bg-warning-bg text-warning",
  danger: "bg-danger-bg text-danger",
  info: "bg-info-bg text-info",
} as const;

type Variant = keyof typeof variants;

export function Badge({
  children,
  variant = "default",
  className,
  dot,
}: {
  children: React.ReactNode;
  variant?: Variant;
  className?: string;
  dot?: boolean;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-caption font-medium",
        variants[variant],
        className,
      )}
    >
      {dot && <span className="h-1.5 w-1.5 rounded-full bg-current shrink-0" />}
      {children}
    </span>
  );
}

export function StatusBadge({ active, activeLabel, inactiveLabel }: { active: boolean; activeLabel: string; inactiveLabel: string }) {
  return (
    <Badge variant={active ? "success" : "default"} dot>
      {active ? activeLabel : inactiveLabel}
    </Badge>
  );
}
