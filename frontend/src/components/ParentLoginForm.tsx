"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { AuthButton } from "@/components/AuthButton";
import { AuthChrome } from "@/components/AuthChrome";
import { GlassInput } from "@/components/GlassInput";
import { apiFetch } from "@/lib/api";

export function ParentLoginForm() {
  const t = useTranslations("parent");
  const [phone, setPhone] = useState("+998");
  const [otp, setOtp] = useState("");
  const [step, setStep] = useState<"phone" | "otp">("phone");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const requestOtp = async () => {
    setLoading(true);
    setError("");
    const res = await apiFetch("/auth/parent/request-otp", {
      method: "POST",
      body: JSON.stringify({ phone }),
    });
    setLoading(false);
    if (res.success) {
      setStep("otp");
    } else {
      setError(t(`errors.${res.error?.code || "UNKNOWN"}`));
    }
  };

  const verifyOtp = async () => {
    setLoading(true);
    setError("");
    const res = await apiFetch<{ access_token: string }>("/auth/parent/verify-otp", {
      method: "POST",
      body: JSON.stringify({ phone, otp }),
    });
    setLoading(false);
    if (res.success && res.data?.access_token) {
      localStorage.setItem("tmb_access_token", res.data.access_token);
      window.location.href = "/parent/dashboard";
    } else {
      setError(t(`errors.${res.error?.code || "UNKNOWN"}`));
    }
  };

  return (
    <AuthChrome
      alternateHref="/"
      alternateLabel={t("staffLogin")}
      heroTitle={t("title")}
      heroSubtitle={t("subtitle")}
    >
      <div className="aeline-split-login__form">
        <h2 className="aeline-split-login__title">{t("title")}</h2>
        <p className="aeline-split-login__hint">{t("subtitle")}</p>

        {step === "phone" ? (
          <div>
            <GlassInput
              label={t("phone")}
              type="tel"
              value={phone}
              onChange={setPhone}
              autoComplete="tel"
              id="parent-phone"
              variant="split"
            />
            {error && (
              <p className="aeline-alert aeline-alert--error aeline-split-login__alert" role="alert">
                {error}
              </p>
            )}
            <div className="aeline-split-login__actions">
              <AuthButton type="button" onClick={requestOtp} disabled={loading || phone.length < 13} variant="split">
                {loading ? t("sending") : t("sendOtp")}
              </AuthButton>
            </div>
          </div>
        ) : (
          <div>
            <GlassInput
              label={t("otp")}
              value={otp}
              onChange={setOtp}
              inputMode="numeric"
              maxLength={6}
              id="parent-otp"
              variant="split"
              className="[&_input]:tracking-[0.35em] [&_input]:text-center"
            />
            {error && (
              <p className="aeline-alert aeline-alert--error aeline-split-login__alert" role="alert">
                {error}
              </p>
            )}
            <div className="aeline-split-login__actions">
              <AuthButton type="button" onClick={verifyOtp} disabled={loading || otp.length < 4} variant="split">
                {loading ? t("verifying") : t("verify")}
              </AuthButton>
            </div>
            <button type="button" onClick={() => setStep("phone")} className="aeline-split-login__forgot aeline-split-login__forgot--center">
              {t("changePhone")}
            </button>
          </div>
        )}
      </div>
    </AuthChrome>
  );
}
