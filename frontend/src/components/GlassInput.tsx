"use client";

import { useId, useState } from "react";
import { useTranslations } from "next-intl";

type GlassInputProps = {
  label: string;
  type?: string;
  value: string;
  onChange: (value: string) => void;
  autoComplete?: string;
  inputMode?: "text" | "numeric" | "tel";
  maxLength?: number;
  className?: string;
  id?: string;
  variant?: "dark" | "light" | "split";
  passwordToggle?: boolean;
  required?: boolean;
};

function PasswordToggleButton({
  visible,
  onToggle,
  labelShow,
  labelHide,
}: {
  visible: boolean;
  onToggle: () => void;
  labelShow: string;
  labelHide: string;
}) {
  return (
    <button
      type="button"
      className="aeline-input-toggle"
      onClick={onToggle}
      aria-label={visible ? labelHide : labelShow}
      aria-pressed={visible}
    >
      {visible ? (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden>
          <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94" />
          <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19" />
          <line x1="1" y1="1" x2="23" y2="23" />
        </svg>
      ) : (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden>
          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
          <circle cx="12" cy="12" r="3" />
        </svg>
      )}
    </button>
  );
}

export function GlassInput({
  label,
  type = "text",
  value,
  onChange,
  autoComplete,
  inputMode,
  maxLength,
  className = "",
  id: externalId,
  variant = "light",
  passwordToggle = false,
  required = true,
}: GlassInputProps) {
  const generatedId = useId();
  const id = externalId ?? generatedId;
  const tAuth = useTranslations("auth");
  const [showPassword, setShowPassword] = useState(false);
  const isPassword = type === "password";
  const inputType = isPassword && passwordToggle && showPassword ? "text" : type;

  if (variant === "split") {
    return (
      <div className={`aeline-split-login__group ${isPassword && passwordToggle ? "aeline-split-login__group--password" : ""} ${className}`}>
        <label htmlFor={id}>{label}</label>
        <div className="aeline-split-login__control-wrap">
          <input
            id={id}
            type={inputType}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            autoComplete={autoComplete}
            inputMode={inputMode}
            maxLength={maxLength}
            className="aeline-split-login__control"
            required={required}
          />
          {isPassword && passwordToggle && (
            <PasswordToggleButton
              visible={showPassword}
              onToggle={() => setShowPassword((v) => !v)}
              labelShow={tAuth("showPassword")}
              labelHide={tAuth("hidePassword")}
            />
          )}
        </div>
      </div>
    );
  }

  if (variant === "light") {
    return (
      <div className={`aeline-input ${isPassword && passwordToggle ? "aeline-input--password" : ""} ${className}`}>
        <input
          id={id}
          type={inputType}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          autoComplete={autoComplete}
          inputMode={inputMode}
          maxLength={maxLength}
          placeholder=" "
          required={required}
        />
        <label htmlFor={id}>{label}</label>
        {isPassword && passwordToggle && (
          <PasswordToggleButton
            visible={showPassword}
            onToggle={() => setShowPassword((v) => !v)}
            labelShow={tAuth("showPassword")}
            labelHide={tAuth("hidePassword")}
          />
        )}
      </div>
    );
  }

  return (
    <div className={`relative border-b-2 border-white/30 py-1 ${className}`}>
      <input
        id={id}
        type={inputType}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        autoComplete={autoComplete}
        inputMode={inputMode}
        maxLength={maxLength}
        placeholder=" "
        required={required}
        className="peer w-full bg-transparent border-none outline-none text-white text-base pt-5 pb-2 placeholder-transparent"
      />
      <label
        htmlFor={id}
        className="absolute left-0 top-1/2 -translate-y-1/2 text-white/80 text-base pointer-events-none transition-all duration-150 peer-focus:top-2 peer-focus:text-xs peer-focus:-translate-y-full peer-focus:text-naqsh-accent peer-[:not(:placeholder-shown)]:top-2 peer-[:not(:placeholder-shown)]:text-xs peer-[:not(:placeholder-shown)]:-translate-y-full"
      >
        {label}
      </label>
    </div>
  );
}
