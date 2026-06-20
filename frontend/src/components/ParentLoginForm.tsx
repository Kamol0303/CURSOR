"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import Link from "next/link";
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
      localStorage.setItem("tamor_access_token", res.data.access_token);
      window.location.href = "/parent/dashboard";
    } else {
      setError(t(`errors.${res.error?.code || "UNKNOWN"}`));
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-lg p-8 border">
        <h1 className="text-2xl font-bold text-naqsh-primary mb-1">{t("title")}</h1>
        <p className="text-sm text-gray-600 mb-6">{t("subtitle")}</p>

        {step === "phone" ? (
          <div className="space-y-4">
            <label className="block text-sm font-medium text-gray-700">{t("phone")}</label>
            <input
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className="w-full border rounded-lg px-3 py-2"
              placeholder="+998901234567"
            />
            <button
              type="button"
              onClick={requestOtp}
              disabled={loading || phone.length < 13}
              className="w-full bg-naqsh-primary text-white py-2 rounded-lg hover:opacity-90 disabled:opacity-50"
            >
              {loading ? t("sending") : t("sendOtp")}
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            <label className="block text-sm font-medium text-gray-700">{t("otp")}</label>
            <input
              type="text"
              value={otp}
              onChange={(e) => setOtp(e.target.value)}
              className="w-full border rounded-lg px-3 py-2 tracking-widest"
              placeholder="123456"
              maxLength={6}
            />
            <button
              type="button"
              onClick={verifyOtp}
              disabled={loading || otp.length < 4}
              className="w-full bg-naqsh-primary text-white py-2 rounded-lg hover:opacity-90 disabled:opacity-50"
            >
              {loading ? t("verifying") : t("verify")}
            </button>
            <button type="button" onClick={() => setStep("phone")} className="text-sm text-gray-500 hover:underline">
              {t("changePhone")}
            </button>
          </div>
        )}

        {error && <p className="mt-4 text-sm text-red-600">{error}</p>}

        <p className="mt-6 text-center text-sm text-gray-500">
          <Link href="/" className="text-naqsh-accent hover:underline">
            {t("staffLogin")}
          </Link>
        </p>
      </div>
    </div>
  );
}
