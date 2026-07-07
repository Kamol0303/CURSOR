import { cn } from "@/lib/cn";
import type { InputHTMLAttributes } from "react";

export const inputClassName = cn(
  "w-full h-10 px-3.5 text-body rounded-lg",
  "bg-surface dark:bg-card border border-border",
  "text-foreground placeholder:text-muted-foreground",
  "shadow-sm transition-all duration-fast ease-out",
  "hover:border-border-strong",
  "focus:outline-none focus:ring-2 focus:ring-naqsh-primary/20 focus:border-naqsh-primary/50",
  "dark:focus:ring-naqsh-accent/20 dark:focus:border-naqsh-accent/50",
  "disabled:opacity-50 disabled:cursor-not-allowed",
);

export type InputProps = InputHTMLAttributes<HTMLInputElement> & {
  error?: boolean;
};

export function Input({ className, error, ...props }: InputProps) {
  return (
    <input
      className={cn(inputClassName, error && "border-danger focus:ring-danger/20 focus:border-danger", className)}
      {...props}
    />
  );
}
