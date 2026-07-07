"use client";

import { useId } from "react";

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
};

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
}: GlassInputProps) {
  const generatedId = useId();
  const id = externalId ?? generatedId;

  return (
    <div className={`relative border-b-2 border-white/30 py-1 ${className}`}>
      <input
        id={id}
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        autoComplete={autoComplete}
        inputMode={inputMode}
        maxLength={maxLength}
        placeholder=" "
        required
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
