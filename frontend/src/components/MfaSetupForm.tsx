"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";

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
  variant?: "default" | "glass";
  onComplete: (accessToken?: string) => void;
  onError: (code: string) => void;
};

export function MfaSetupForm({ setupToken, accessToken, variant = "default", onComplete, onError }: Props) {
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
    return <p className={`text-sm ${variant === "glass" ? "text-white/70" : "text-gray-500"}`}>{t("mfaSetupLoading")}</p>;
  }

  if (!setup) {
    return null;
  }

  const isGlass = variant === "glass";

  return (
    <form onSubmit={handleConfirm} className="space-y-4">
      <h2 className={`font-semibold text-center ${isGlass ? "text-white text-xl" : "text-naqsh-primary"}`}>
        {t("mfaSetupTitle")}
      </h2>
      <p className={`text-sm ${isGlass ? "text-white/70" : "text-gray-600 dark:text-gray-400"}`}>
        {t("mfaSetupInstructions")}
      </p>
      <div
        className={`rounded-lg p-3 text-sm font-mono break-all ${
          isGlass ? "bg-white/10 border border-white/15 text-white" : "bg-gray-50 dark:bg-gray-800"
        }`}
      >
        <div className={`text-xs mb-1 ${isGlass ? "text-white/55" : "text-gray-500"}`}>{t("mfaSetupSecret")}</div>
        {setup.secret}
      </div>
      <details className={`text-xs ${isGlass ? "text-white/55" : "text-gray-500"}`}>
        <summary className="cursor-pointer">{t("mfaSetupAdvanced")}</summary>
        <p className="mt-2 break-all font-mono">{setup.provisioning_uri}</p>
      </details>
      <div>
        {isGlass ? (
          <div className="relative border-b-2 border-white/30 py-1">
            <input
              id="mfa-setup-code"
              type="text"
              inputMode="numeric"
              autoComplete="one-time-code"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder=" "
              required
              className="peer w-full bg-transparent border-none outline-none text-white text-base pt-5 pb-2 tracking-widest text-center placeholder-transparent"
            />
            <label
              htmlFor="mfa-setup-code"
              className="absolute left-0 top-1/2 -translate-y-1/2 text-white/80 text-base pointer-events-none transition-all duration-150 peer-focus:top-2 peer-focus:text-xs peer-focus:-translate-y-full peer-focus:text-naqsh-accent peer-[:not(:placeholder-shown)]:top-2 peer-[:not(:placeholder-shown)]:text-xs peer-[:not(:placeholder-shown)]:-translate-y-full"
            >
              {t("mfaCode")}
            </label>
          </div>
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
      <button
        type="submit"
        disabled={loading}
        className={
          isGlass
            ? "w-full bg-white text-gray-900 font-semibold py-3 rounded-md border-2 border-transparent hover:text-white hover:border-white hover:bg-white/15 transition-all duration-300 disabled:opacity-50"
            : "w-full py-2.5 bg-naqsh-accent text-white rounded-lg font-medium hover:opacity-90 disabled:opacity-50 transition-colors"
        }
      >
        {t("mfaSetupConfirm")}
      </button>
    </form>
  );
}
