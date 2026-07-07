"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { AuthChrome } from "@/components/AuthChrome";
import { GlassInput } from "@/components/GlassInput";
import { GridGlowEffect } from "@/components/GridGlowEffect";
import { TmbLogo } from "@/components/TmbLogo";
import { apiFetch } from "@/lib/api";

const glassBtn =
  "w-full bg-white text-gray-900 font-semibold py-3 rounded-md border-2 border-transparent hover:text-white hover:border-white hover:bg-white/15 transition-all duration-300 disabled:opacity-50 text-base";

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
      <div className="text-left">
        <div className="flex justify-center mb-5 lg:hidden">
          <div className="relative w-16 h-16 rounded-2xl overflow-hidden border border-white/20">
            <GridGlowEffect className="inset-0" columns={6} rows={6} compact color="#c8932a" />
            <div className="absolute inset-0 flex items-center justify-center z-10 pointer-events-none">
              <TmbLogo className="w-9 h-9 text-naqsh-accent auth-logo-float" />
            </div>
          </div>
        </div>

        <h2 className="text-2xl font-semibold text-white text-center mb-1">{t("title")}</h2>
        <p className="text-xs text-white/60 text-center mb-6">{t("subtitle")}</p>

        {step === "phone" ? (
          <div className="flex flex-col">
            <GlassInput
              label={t("phone")}
              type="tel"
              value={phone}
              onChange={setPhone}
              autoComplete="tel"
              id="parent-phone"
            />
            {error && (
              <p className="text-sm text-red-200 mt-4" role="alert">
                {error}
              </p>
            )}
            <button
              type="button"
              onClick={requestOtp}
              disabled={loading || phone.length < 13}
              className={`${glassBtn} mt-7`}
            >
              {loading ? t("sending") : t("sendOtp")}
            </button>
          </div>
        ) : (
          <div className="flex flex-col">
            <GlassInput
              label={t("otp")}
              value={otp}
              onChange={setOtp}
              inputMode="numeric"
              maxLength={6}
              id="parent-otp"
              className="[&_input]:tracking-[0.35em] [&_input]:text-center"
            />
            {error && (
              <p className="text-sm text-red-200 mt-4" role="alert">
                {error}
              </p>
            )}
            <button
              type="button"
              onClick={verifyOtp}
              disabled={loading || otp.length < 4}
              className={`${glassBtn} mt-7`}
            >
              {loading ? t("verifying") : t("verify")}
            </button>
            <button
              type="button"
              onClick={() => setStep("phone")}
              className="mt-4 text-sm text-white/70 hover:text-white hover:underline text-center"
            >
              {t("changePhone")}
            </button>
          </div>
        )}
      </div>
    </AuthChrome>
  );
}
