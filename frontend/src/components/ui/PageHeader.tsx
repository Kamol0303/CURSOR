import { cn } from "@/lib/cn";

export function PageHeader({
  title,
  description,
  actions,
  className,
}: {
  title: string;
  description?: string;
  actions?: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4", className)}>
      <div className="min-w-0">
        <h1 className="text-h2 text-naqsh-primary dark:text-naqsh-accent tracking-tight">{title}</h1>
        {description && (
          <p className="text-small text-muted-foreground mt-1">{description}</p>
        )}
      </div>
      {actions && (
        <div className="flex flex-wrap items-center gap-2 shrink-0">{actions}</div>
      )}
    </div>
  );
}

export function PageSection({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return <section className={cn("space-y-6 animate-slide-up", className)}>{children}</section>;
}
