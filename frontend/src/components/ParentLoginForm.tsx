"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { AuthButton } from "@/components/AuthButton";
import { AuthChrome } from "@/components/AuthChrome";
import { GlassInput } from "@/components/GlassInput";
import { apiFetch } from "@/lib/api";
import { setAuthCookie } from "@/lib/auth-cookie";
import { displayUzPhone, formatUzPhone, isValidUzPhone } from "@/lib/phone";

const OTP_RESEND_SECONDS = 60;

export function ParentLoginForm() {
  const t = useTranslations("parent");
  const [phone, setPhone] = useState("+998");
  const [otp, setOtp] = useState("");
  const [step, setStep] = useState<"phone" | "otp">("phone");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [resendIn, setResendIn] = useState(0);

  useEffect(() => {
    if (resendIn <= 0) return;
    const timer = window.setInterval(() => {
      setResendIn((s) => (s <= 1 ? 0 : s - 1));
    }, 1000);
    return () => window.clearInterval(timer);
  }, [resendIn]);

  const normalizedPhone = formatUzPhone(phone);

  const requestOtp = async () => {
    if (!isValidUzPhone(normalizedPhone)) {
      setError(t("errors.PHONE_INVALID"));
      return;
    }
    setLoading(true);
    setError("");
    const res = await apiFetch("/auth/parent/request-otp", {
      method: "POST",
      body: JSON.stringify({ phone: normalizedPhone }),
    });
    setLoading(false);
    if (res.success) {
      setPhone(normalizedPhone);
      setStep("otp");
      setResendIn(OTP_RESEND_SECONDS);
    } else {
      setError(t(`errors.${res.error?.code || "UNKNOWN"}`));
    }
  };

  const verifyOtp = async () => {
    setLoading(true);
    setError("");
    const res = await apiFetch<{ access_token: string }>("/auth/parent/verify-otp", {
      method: "POST",
      body: JSON.stringify({ phone: normalizedPhone, otp }),
    });
    setLoading(false);
    if (res.success && res.data?.access_token) {
      localStorage.setItem("tmb_access_token", res.data.access_token);
      setAuthCookie(res.data.access_token);
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
              value={displayUzPhone(phone)}
              onChange={(v) => setPhone(formatUzPhone(v))}
              autoComplete="tel"
              id="parent-phone"
              variant="split"
              maxLength={17}
            />
            {error && (
              <p className="aeline-alert aeline-alert--error aeline-split-login__alert" role="alert">
                {error}
              </p>
            )}
            <div className="aeline-split-login__actions">
              <AuthButton
                type="button"
                onClick={requestOtp}
                disabled={loading || !isValidUzPhone(normalizedPhone)}
                variant="split"
              >
                {loading ? t("sending") : t("sendOtp")}
              </AuthButton>
            </div>
          </div>
        ) : (
          <div>
            <p className="aeline-split-login__hint !mt-0 !mb-3">{displayUzPhone(normalizedPhone)}</p>
            <GlassInput
              label={t("otp")}
              value={otp}
              onChange={(v) => setOtp(v.replace(/\D/g, "").slice(0, 6))}
              inputMode="numeric"
              autoComplete="one-time-code"
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
            <div className="aeline-split-login__otp-actions">
              {resendIn > 0 ? (
                <span className="aeline-split-login__resend-timer">{t("resendIn", { seconds: resendIn })}</span>
              ) : (
                <button type="button" onClick={requestOtp} disabled={loading} className="aeline-split-login__forgot">
                  {t("resendOtp")}
                </button>
              )}
              <button
                type="button"
                onClick={() => {
                  setStep("phone");
                  setOtp("");
                  setError("");
                }}
                className="aeline-split-login__forgot"
              >
                {t("changePhone")}
              </button>
            </div>
          </div>
        )}
      </div>
    </AuthChrome>
  );
}
