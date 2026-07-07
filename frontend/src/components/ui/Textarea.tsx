import { cn } from "@/lib/cn";
import type { TextareaHTMLAttributes } from "react";

export const textareaClassName = cn(
  "w-full px-3.5 py-2.5 text-body rounded-lg resize-y min-h-[80px]",
  "bg-surface dark:bg-card border border-border",
  "text-foreground placeholder:text-muted-foreground",
  "shadow-sm transition-all duration-fast ease-out",
  "hover:border-border-strong",
  "focus:outline-none focus:ring-2 focus:ring-naqsh-primary/20 focus:border-naqsh-primary/50",
  "dark:focus:ring-naqsh-accent/20 dark:focus:border-naqsh-accent/50",
  "disabled:opacity-50 disabled:cursor-not-allowed",
);

export type TextareaProps = TextareaHTMLAttributes<HTMLTextAreaElement>;

export function Textarea({ className, ...props }: TextareaProps) {
  return <textarea className={cn(textareaClassName, className)} {...props} />;
}
