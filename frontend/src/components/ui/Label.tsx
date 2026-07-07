import { cn } from "@/lib/cn";
import type { LabelHTMLAttributes } from "react";

export type LabelProps = LabelHTMLAttributes<HTMLLabelElement> & {
  required?: boolean;
};

export function Label({ className, required, children, ...props }: LabelProps) {
  return (
    <label
      className={cn("block text-label text-foreground-secondary mb-1.5", className)}
      {...props}
    >
      {children}
      {required && <span className="text-danger ml-0.5" aria-hidden>*</span>}
    </label>
  );
}

export function FormField({ className, children }: { className?: string; children: React.ReactNode }) {
  return <div className={cn("space-y-1.5", className)}>{children}</div>;
}

export function FormGrid({ className, children }: { className?: string; children: React.ReactNode }) {
  return <div className={cn("grid grid-cols-1 sm:grid-cols-2 gap-4", className)}>{children}</div>;
}

export function FormActions({ className, children }: { className?: string; children: React.ReactNode }) {
  return (
    <div className={cn("flex flex-wrap items-center justify-end gap-2 pt-2", className)}>
      {children}
    </div>
  );
}
