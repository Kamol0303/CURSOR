"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";

import { getApiBaseUrl } from "@/lib/api";

type SetupData = {
  provisioning_uri: string;
  secret: string;
  issuer: string;
};

type Props = {
  setupToken?: string;
  accessToken?: string;
  onComplete: (accessToken?: string) => void;
  onError: (code: string) => void;
};

export function MfaSetupForm({ setupToken, accessToken, onComplete, onError }: Props) {
  const t = useTranslations("auth");
  const [setup, setSetup] = useState<SetupData | null>(null);
  const [code, setCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [initLoading, setInitLoading] = useState(true);

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
    } catch {
      onError("MFA_INVALID");
    } finally {
      setLoading(false);
    }
  };

  if (initLoading) {
    return <p className="text-sm text-gray-500">{t("mfaSetupLoading")}</p>;
  }

  if (!setup) {
    return null;
  }

  return (
    <form onSubmit={handleConfirm} className="space-y-4">
      <h2 className="font-semibold text-naqsh-primary">{t("mfaSetupTitle")}</h2>
      <p className="text-sm text-gray-600 dark:text-gray-400">{t("mfaSetupInstructions")}</p>
      <div className="rounded-lg bg-gray-50 dark:bg-gray-800 p-3 text-sm font-mono break-all">
        <div className="text-xs text-gray-500 mb-1">{t("mfaSetupSecret")}</div>
        {setup.secret}
      </div>
      <details className="text-xs text-gray-500">
        <summary className="cursor-pointer">{t("mfaSetupAdvanced")}</summary>
        <p className="mt-2 break-all font-mono">{setup.provisioning_uri}</p>
      </details>
      <div>
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
      </div>
      <button
        type="submit"
        disabled={loading}
        className="w-full py-2.5 bg-naqsh-accent text-white rounded-lg font-medium hover:opacity-90 disabled:opacity-50 transition-colors"
      >
        {t("mfaSetupConfirm")}
      </button>
    </form>
  );
}
