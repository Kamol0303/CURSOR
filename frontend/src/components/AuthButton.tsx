"use client";

type AuthButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary";
  fullWidth?: boolean;
};

export function AuthButton({
  variant = "primary",
  fullWidth = true,
  className = "",
  children,
  type = "button",
  ...props
}: AuthButtonProps) {
  const wrapClass =
    variant === "primary" ? "auth-af-btn-border is-primary" : "auth-af-btn-border is-secondary";

  return (
    <span className={`${wrapClass} ${fullWidth ? "auth-af-btn-border--block" : ""} ${className}`}>
      <button type={type} className={`auth-af-btn ${variant === "primary" ? "is-primary" : "is-secondary"}`} {...props}>
        <span className="auth-af-btn__label">{children}</span>
        <span className="auth-af-btn-glow auth-af-btn-glow--inner" aria-hidden />
      </button>
      <span className="auth-af-btn-glow auth-af-btn-glow--outer" aria-hidden />
    </span>
  );
}
