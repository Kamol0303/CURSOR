"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { MfaSetupForm } from "@/components/MfaSetupForm";
import { ChangePasswordForm } from "@/components/ChangePasswordForm";
import { AdminResetPasswordForm } from "@/components/AdminResetPasswordForm";
import { IssueCredentialsForm } from "@/components/IssueCredentialsForm";
import { PermissionGate } from "@/components/PermissionGate";
import { getApiBaseUrl, getToken } from "@/lib/api";

export default function SecurityPage() {
  const t = useTranslations("security");
  const [mfaEnabled, setMfaEnabled] = useState(false);
  const [mfaRequired, setMfaRequired] = useState(false);
  const [showSetup, setShowSetup] = useState(false);
  const [backupCodes, setBackupCodes] = useState<string[] | null>(null);
  const [regenerating, setRegenerating] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    import("@/lib/api").then(({ getMe }) => {
      getMe().then((me) => {
        if (!me.success) return;
        setMfaEnabled(me.data.mfa_enabled);
        setMfaRequired(me.data.mfa_required ?? false);
      });
    });
  }, []);

  const regenerateBackupCodes = async () => {
    setRegenerating(true);
    setError(null);
    setMessage(null);
    setBackupCodes(null);
    try {
      const token = getToken();
      const res = await fetch(`${getApiBaseUrl()}/api/v1/auth/mfa/backup-codes/regenerate`, {
        method: "POST",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        credentials: "include",
      });
      const data = await res.json();
      if (!res.ok) {
        setError(t(`errors.${data.detail?.code || "MFA_NOT_CONFIGURED"}` as "errors.MFA_INVALID"));
        return;
      }
      setBackupCodes(data.data?.backup_codes || []);
      setMessage(t("backupCodesRegenerated"));
    } catch {
      setError(t("errors.MFA_INVALID"));
    } finally {
      setRegenerating(false);
    }
  };

  return (
    <div className="max-w-lg space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">{t("title")}</h2>
        <p className="text-gray-500 mt-1">{t("subtitle")}</p>
      </div>

      <div className="bg-white rounded-xl border p-6 space-y-4">
        <ChangePasswordForm />
      </div>

      <PermissionGate permission="users.password_reset">
        <div className="bg-white rounded-xl border p-6">
          <AdminResetPasswordForm />
        </div>
      </PermissionGate>

      <PermissionGate permission="security.credentials.issue">
        <div className="bg-white rounded-xl border p-6">
          <IssueCredentialsForm />
        </div>
      </PermissionGate>

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

        {mfaEnabled && (
          <div className="space-y-2 pt-2 border-t">
            <p className="text-sm text-gray-600">{t("backupCodesHint")}</p>
            <button
              type="button"
              onClick={regenerateBackupCodes}
              disabled={regenerating}
              className="px-4 py-2 border rounded-lg text-sm hover:bg-gray-50 disabled:opacity-50"
            >
              {regenerating ? t("backupCodesRegenerating") : t("regenerateBackupCodes")}
            </button>
            {backupCodes && (
              <div className="rounded-lg bg-amber-50 border border-amber-200 p-3">
                <p className="text-xs font-semibold text-amber-900 mb-2">{t("backupCodesOnce")}</p>
                <ul className="font-mono text-sm space-y-1">
                  {backupCodes.map((code) => (
                    <li key={code}>{code}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {message && <p className="text-sm text-green-700">{message}</p>}
        {error && (
          <p className="text-sm text-red-600" role="alert">
            {error}
          </p>
        )}
      </div>
    </div>
  );
}
