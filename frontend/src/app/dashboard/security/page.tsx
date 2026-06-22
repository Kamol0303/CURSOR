"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { DashboardLayout } from "@/components/DashboardLayout";
import { MfaSetupForm } from "@/components/MfaSetupForm";
import { getMe, getToken } from "@/lib/api";

export default function SecurityPage() {
  const t = useTranslations("security");
  const [mfaEnabled, setMfaEnabled] = useState(false);
  const [mfaRequired, setMfaRequired] = useState(false);
  const [showSetup, setShowSetup] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      window.location.href = "/";
      return;
    }
    getMe().then((me) => {
      if (!me.success) return;
      setMfaEnabled(me.data.mfa_enabled);
      setMfaRequired(me.data.mfa_required ?? false);
    });
  }, []);

  return (
    <DashboardLayout>
      <div className="max-w-lg space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">{t("title")}</h2>
          <p className="text-gray-500 mt-1">{t("subtitle")}</p>
        </div>

        <div className="bg-white rounded-xl border p-6 space-y-4">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="font-semibold">{t("mfaLabel")}</h3>
              <p className="text-sm text-gray-500">
                {mfaEnabled ? t("mfaEnabled") : t("mfaDisabled")}
                {mfaRequired && ` · ${t("mfaRequired")}`}
              </p>
            </div>
            <span
              className={`px-2 py-1 rounded text-xs font-medium ${
                mfaEnabled ? "bg-green-100 text-green-800" : "bg-amber-100 text-amber-800"
              }`}
            >
              {mfaEnabled ? t("statusOn") : t("statusOff")}
            </span>
          </div>

          {!mfaEnabled && !showSetup && (
            <button
              type="button"
              onClick={() => {
                setShowSetup(true);
                setError(null);
                setMessage(null);
              }}
              className="px-4 py-2 bg-naqsh-primary text-white rounded-lg text-sm font-medium hover:bg-naqsh-primary/90"
            >
              {t("enableMfa")}
            </button>
          )}

          {showSetup && !mfaEnabled && (
            <MfaSetupForm
              accessToken={getToken() || undefined}
              onComplete={() => {
                setMfaEnabled(true);
                setShowSetup(false);
                setMessage(t("mfaEnabledSuccess"));
              }}
              onError={(code) => setError(t(`errors.${code}` as "errors.MFA_INVALID"))}
            />
          )}

          {message && <p className="text-sm text-green-700">{message}</p>}
          {error && (
            <p className="text-sm text-red-600" role="alert">
              {error}
            </p>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
