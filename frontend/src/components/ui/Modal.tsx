"use client";

import { useEffect, useCallback } from "react";
import { cn } from "@/lib/cn";
import { Button } from "./Button";

type ModalProps = {
  open?: boolean;
  onClose: () => void;
  title?: React.ReactNode;
  description?: React.ReactNode;
  children: React.ReactNode;
  size?: "sm" | "md" | "lg" | "xl";
  showClose?: boolean;
  className?: string;
  footer?: React.ReactNode;
};

const sizes = {
  sm: "max-w-md",
  md: "max-w-lg",
  lg: "max-w-2xl",
  xl: "max-w-4xl",
};

export function Modal({
  open = true,
  onClose,
  title,
  description,
  children,
  size = "md",
  showClose = true,
  className,
  footer,
}: ModalProps) {
  const handleEscape = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    },
    [onClose],
  );

  useEffect(() => {
    if (!open) return;
    document.body.style.overflow = "hidden";
    document.addEventListener("keydown", handleEscape);
    return () => {
      document.body.style.overflow = "";
      document.removeEventListener("keydown", handleEscape);
    };
  }, [open, handleEscape]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-4 sm:p-6"
      role="dialog"
      aria-modal="true"
      aria-labelledby={title ? "modal-title" : undefined}
    >
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-[2px] animate-fade-in"
        onClick={onClose}
        aria-hidden
      />
      <div
        className={cn(
          "relative w-full bg-card rounded-2xl shadow-xl border border-border",
          "max-h-[90vh] flex flex-col animate-scale-in",
          sizes[size],
          className,
        )}
      >
        {(title || showClose) && (
          <div className="flex items-start justify-between gap-4 px-6 pt-5 pb-4 border-b border-border shrink-0">
            <div className="min-w-0">
              {title && (
                <h2 id="modal-title" className="text-h3 text-naqsh-primary dark:text-naqsh-accent">
                  {title}
                </h2>
              )}
              {description && (
                <p className="text-small text-muted-foreground mt-1">{description}</p>
              )}
            </div>
            {showClose && (
              <button
                type="button"
                onClick={onClose}
                className="shrink-0 p-1.5 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted transition-colors duration-fast"
                aria-label="Close"
              >
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
          </div>
        )}
        <div className="overflow-y-auto flex-1 px-6 py-5 scrollbar-thin">{children}</div>
        {footer && (
          <div className="px-6 py-4 border-t border-border shrink-0 flex justify-end gap-2">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
}

export function ModalFooter({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}

export function ModalCancelButton({ onClick, children }: { onClick: () => void; children: React.ReactNode }) {
  return (
    <Button type="button" variant="secondary" onClick={onClick}>
      {children}
    </Button>
  );
}

export function ModalSubmitButton({
  loading,
  children,
  form,
}: {
  loading?: boolean;
  children: React.ReactNode;
  form?: string;
}) {
  return (
    <Button type="submit" loading={loading} form={form}>
      {children}
    </Button>
  );
}
