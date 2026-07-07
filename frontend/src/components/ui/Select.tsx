import { cn } from "@/lib/cn";
import type { SelectHTMLAttributes } from "react";

export const selectClassName = cn(
  "w-full h-10 px-3.5 text-body rounded-lg appearance-none",
  "bg-surface dark:bg-card border border-border",
  "text-foreground shadow-sm transition-all duration-fast ease-out",
  "hover:border-border-strong",
  "focus:outline-none focus:ring-2 focus:ring-naqsh-primary/20 focus:border-naqsh-primary/50",
  "dark:focus:ring-naqsh-accent/20 dark:focus:border-naqsh-accent/50",
  "disabled:opacity-50 disabled:cursor-not-allowed",
);

export type SelectProps = SelectHTMLAttributes<HTMLSelectElement>;

export function Select({ className, children, ...props }: SelectProps) {
  return (
    <div className="relative">
      <select className={cn(selectClassName, "pr-9", className)} {...props}>
        {children}
      </select>
      <svg
        className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        aria-hidden
      >
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
      </svg>
    </div>
  );
}
