import { cn } from "@/lib/cn";

export function Card({
  className,
  children,
  hover,
}: {
  className?: string;
  children: React.ReactNode;
  hover?: boolean;
}) {
  return (
    <div
      className={cn(
        "bg-card rounded-xl border border-border shadow-sm shadow-inset-highlight",
        hover && "transition-all duration-slow ease-premium hover:shadow-md hover:-translate-y-px",
        className,
      )}
    >
      {children}
    </div>
  );
}

/** Double-bezel shell (taste-skill / high-end-visual-design). */
export function BezelCard({
  className,
  children,
  hover,
  padding = "p-1.5",
}: {
  className?: string;
  children: React.ReactNode;
  hover?: boolean;
  padding?: string;
}) {
  return (
    <div
      className={cn(
        "rounded-2xl bg-muted/80 ring-1 ring-border/80",
        padding,
        hover && "transition-all duration-slow ease-premium hover:shadow-md",
        className,
      )}
    >
      <div
        className={cn(
          "rounded-[calc(1rem-0.125rem)] bg-card border border-border/60 shadow-sm shadow-inset-highlight",
          hover && "transition-shadow duration-slow ease-premium",
        )}
      >
        {children}
      </div>
    </div>
  );
}

export function CardHeader({ className, children }: { className?: string; children: React.ReactNode }) {
  return <div className={cn("px-5 py-4 border-b border-border", className)}>{children}</div>;
}

export function CardBody({ className, children }: { className?: string; children: React.ReactNode }) {
  return <div className={cn("p-5", className)}>{children}</div>;
}

export function CardTitle({ className, children }: { className?: string; children: React.ReactNode }) {
  return <h3 className={cn("text-h4 text-foreground text-balance", className)}>{children}</h3>;
}

export function CardDescription({ className, children }: { className?: string; children: React.ReactNode }) {
  return <p className={cn("text-small text-muted-foreground mt-0.5 max-w-[65ch]", className)}>{children}</p>;
}
