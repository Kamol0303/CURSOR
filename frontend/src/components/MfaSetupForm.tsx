"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { AuthButton } from "@/components/AuthButton";
import { GlassInput } from "@/components/GlassInput";

import { getApiBaseUrl } from "@/lib/api";
import { setAuthCookie } from "@/lib/auth-cookie";

type SetupData = {
  provisioning_uri: string;
  secret: string;
  issuer: string;
};

type Props = {
  setupToken?: string;
  accessToken?: string;
  variant?: "default" | "glass" | "light";
  onComplete: (accessToken?: string) => void;
  onError: (code: string) => void;
};

export function MfaSetupForm({ setupToken, accessToken, variant = "default", onComplete, onError }: Props) {
  const t = useTranslations("auth");
  const [setup, setSetup] = useState<SetupData | null>(null);
  const [code, setCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [initLoading, setInitLoading] = useState(true);

  const isLight = variant === "light" || variant === "glass";

  useEffect(() => {
    const init = async () => {
      try {
        const headers: Record<string, string> = { "Content-Type": "application/json" };
        if (accessToken) headers.Authorization = `Bearer ${accessToken}`;

        const res = await fetch(`${getApiBaseUrl()}/api/v1/auth/mfa/setup/init`, {
          method: "POST",
          headers,
          credentials: "include",
          body: JSON.stringify(setupToken ? { setup_token: setupToken } : {}),
        });
        const data = await res.json();
        if (!res.ok) {
          onError(data.detail?.code || "MFA_SETUP_EXPIRED");
          return;
        }
        setSetup(data.data);
      } catch {
        onError("MFA_SETUP_EXPIRED");
      } finally {
        setInitLoading(false);
      }
    };
    init();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [setupToken, accessToken]);

  const handleConfirm = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const headers: Record<string, string> = { "Content-Type": "application/json" };
      if (accessToken) headers.Authorization = `Bearer ${accessToken}`;

      const res = await fetch(`${getApiBaseUrl()}/api/v1/auth/mfa/setup/confirm`, {
        method: "POST",
        headers,
        credentials: "include",
        body: JSON.stringify({
          code,
          ...(setupToken ? { setup_token: setupToken } : {}),
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        onError(data.detail?.code || "MFA_INVALID");
        return;
      }
      onComplete(data.data?.access_token);
      if (data.data?.access_token) {
        setAuthCookie(data.data.access_token);
      }
      if (data.data?.backup_codes?.length) {
        window.alert(`Backup kodlar (bir marta ko'rsatiladi):\n${data.data.backup_codes.join("\n")}`);
      }
    } catch {
      onError("MFA_INVALID");
    } finally {
      setLoading(false);
    }
  };

  if (initLoading) {
    return <p className={`text-sm ${isLight ? "text-slate-500" : "text-gray-500"}`}>{t("mfaSetupLoading")}</p>;
  }

  if (!setup) {
    return null;
  }

  return (
    <form onSubmit={handleConfirm} className="space-y-4">
      <h2 className={`font-semibold text-center ${isLight ? "aeline-login-card__title !mb-0" : "text-naqsh-primary"}`}>
        {t("mfaSetupTitle")}
      </h2>
      <p className={`text-sm text-center ${isLight ? "text-slate-500" : "text-gray-600 dark:text-gray-400"}`}>
        {t("mfaSetupInstructions")}
      </p>
      <div
        className={`rounded-lg p-3 text-sm font-mono break-all ${
          isLight ? "bg-slate-50 border border-slate-200 text-slate-800" : "bg-gray-50 dark:bg-gray-800"
        }`}
      >
        <div className={`text-xs mb-1 ${isLight ? "text-slate-500" : "text-gray-500"}`}>{t("mfaSetupSecret")}</div>
        {setup.secret}
      </div>
      <details className={`text-xs ${isLight ? "text-slate-500" : "text-gray-500"}`}>
        <summary className="cursor-pointer">{t("mfaSetupAdvanced")}</summary>
        <p className="mt-2 break-all font-mono">{setup.provisioning_uri}</p>
      </details>
      <div>
        {isLight ? (
          <GlassInput
            label={t("mfaCode")}
            value={code}
            onChange={setCode}
            inputMode="numeric"
            autoComplete="one-time-code"
            id="mfa-setup-code"
            variant="light"
            className="[&_input]:tracking-widest [&_input]:text-center"
          />
        ) : (
          <>
            <label htmlFor="mfa-setup-code" className="block text-sm font-medium mb-1">
              {t("mfaCode")}
            </label>
            <input
              id="mfa-setup-code"
              type="text"
              inputMode="numeric"
              autoComplete="one-time-code"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-naqsh-primary/30 focus:border-naqsh-primary outline-none tracking-widest text-center"
              required
            />
          </>
        )}
      </div>
      {isLight ? (
        <AuthButton type="submit" disabled={loading}>
          {t("mfaSetupConfirm")}
        </AuthButton>
      ) : (
        <button
          type="submit"
          disabled={loading}
          className="w-full py-2.5 bg-naqsh-accent text-white rounded-lg font-medium hover:opacity-90 disabled:opacity-50 transition-colors"
        >
          {t("mfaSetupConfirm")}
        </button>
      )}
    </form>
  );
}
