"use client";

import Link from "next/link";

type AuthButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "dark" | "secondary" | "lime";
  fullWidth?: boolean;
};

export function AuthButton({
  variant = "dark",
  fullWidth = true,
  className = "",
  children,
  type = "button",
  ...props
}: AuthButtonProps) {
  return (
    <button
      type={type}
      className={`aeline-btn aeline-btn--${variant} ${fullWidth ? "aeline-btn--block" : ""} ${className}`}
      {...props}
    >
      <span>{children}</span>
    </button>
  );
}

type AuthArrowButtonProps = {
  href: string;
  children: React.ReactNode;
  variant?: "dark" | "lime";
  className?: string;
};

export function AuthArrowButton({ href, children, variant = "dark", className = "" }: AuthArrowButtonProps) {
  return (
    <Link href={href} className={`aeline-btn-arrow aeline-btn-arrow--${variant} ${className}`}>
      <span className="aeline-btn-arrow__text">{children}</span>
      <span className="aeline-btn-arrow__icon" aria-hidden>
        <svg viewBox="0 0 20 20" fill="none">
          <path
            d="M13.046 8.13L5.873 15.3 4.695 14.13 11.867 6.95H5.546V5.29H14.712v9.17h-1.666V8.13Z"
            fill="currentColor"
          />
        </svg>
      </span>
    </Link>
  );
}
