"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { ThemeToggle } from "@/components/ThemeToggle";
import { MfaSetupForm } from "@/components/MfaSetupForm";
import { TmbLogo } from "@/components/TmbLogo";

import { getApiBaseUrl } from "@/lib/api";
import { getRoleFromToken, homePathForRole, setAuthCookie } from "@/lib/auth-cookie";

type Step = "login" | "mfa" | "mfa_setup";

const inputClass =
  "w-full px-3.5 py-2.5 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800/80 dark:text-gray-100 text-sm shadow-sm focus:ring-2 focus:ring-naqsh-primary/25 focus:border-naqsh-primary outline-none transition-colors";

export function LoginForm() {
  const t = useTranslations("auth");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [step, setStep] = useState<Step>("login");
  const [mfaToken, setMfaToken] = useState<string | null>(null);
  const [setupToken, setSetupToken] = useState<string | null>(null);
  const [mfaCode, setMfaCode] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleError = (code: string) => {
    const key = `errors.${code}` as "errors.INVALID_CREDENTIALS";
    try {
      setError(t(key));
    } catch {
      setError(code);
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${getApiBaseUrl()}/api/v1/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ username: username.trim(), password }),
      });
      let data: {
        success?: boolean;
        data?: {
          access_token?: string;
          requires_mfa?: boolean;
          requires_mfa_setup?: boolean;
          mfa_token?: string;
          setup_token?: string;
        };
        detail?: { code?: string };
        error?: { code?: string };
      };
      try {
        data = await res.json();
      } catch {
        setError(t("errors.NETWORK_ERROR"));
        return;
      }
      if (!res.ok || data.success === false) {
        const code = data.detail?.code || data.error?.code || "INVALID_CREDENTIALS";
        handleError(code);
        return;
      }
      if (data.data?.requires_mfa_setup) {
        setSetupToken(data.data.setup_token ?? null);
        setStep("mfa_setup");
        return;
      }
      if (data.data?.requires_mfa) {
        setMfaToken(data.data.mfa_token ?? null);
        setStep("mfa");
        return;
      }
      if (data.data?.access_token) {
        localStorage.setItem("tmb_access_token", data.data.access_token);
        setAuthCookie(data.data.access_token);
        window.location.href = homePathForRole(getRoleFromToken(data.data.access_token));
        return;
      }
      handleError("INVALID_CREDENTIALS");
    } catch {
      setError(t("errors.NETWORK_ERROR"));
    } finally {
      setLoading(false);
    }
  };

  const handleMfa = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${getApiBaseUrl()}/api/v1/auth/mfa/verify`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ mfa_token: mfaToken, code: mfaCode }),
      });
      const data = await res.json();
      if (!res.ok) {
        handleError(data.detail?.code || "MFA_INVALID");
        return;
      }
      localStorage.setItem("tmb_access_token", data.data.access_token);
      setAuthCookie(data.data.access_token);
      window.location.href = homePathForRole(getRoleFromToken(data.data.access_token));
    } catch {
      setError(t("errors.MFA_INVALID"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen girih-bg flex flex-col">
      <header className="flex justify-between items-center gap-3 px-4 sm:px-6 py-4">
        <div className="flex items-center gap-2 text-naqsh-primary dark:text-naqsh-accent">
          <TmbLogo className="w-8 h-8" />
          <span className="font-semibold text-sm tracking-wide hidden sm:inline">TMB</span>
        </div>
        <div className="flex items-center gap-2">
          <ThemeToggle />
          <LanguageSwitcher />
        </div>
      </header>

      <main className="flex-1 flex items-center justify-center p-4 sm:p-6">
        <div className="w-full max-w-4xl">
          <div className="grid lg:grid-cols-[1fr_1.1fr] rounded-2xl overflow-hidden shadow-2xl border border-naqsh-primary/10 dark:border-white/10 bg-white/95 dark:bg-gray-900/95 backdrop-blur">
            {/* Brand panel */}
            <div className="hidden lg:flex flex-col justify-between bg-gradient-to-br from-[#1b4d3e] via-[#1e3a2f] to-[#163328] text-white p-10 relative overflow-hidden">
              <div className="absolute inset-0 opacity-[0.07] girih-bg pointer-events-none" aria-hidden />
              <div className="relative">
                <TmbLogo className="w-14 h-14 text-naqsh-accent mb-6" />
                <h1 className="text-2xl font-bold leading-tight mb-3">{t("title")}</h1>
                <p className="text-sm text-white/75 leading-relaxed max-w-xs">{t("subtitle")}</p>
              </div>
              <p className="relative text-xs text-white/50 border-t border-white/10 pt-4">
                Toyloq tumani · Samarqand viloyati
              </p>
            </div>

            {/* Form panel */}
            <div className="p-6 sm:p-8 lg:p-10 flex flex-col justify-center border-t-4 border-naqsh-accent lg:border-t-0 lg:border-l-4 lg:border-l-naqsh-accent">
              <div className="lg:hidden flex items-center gap-3 mb-6">
                <TmbLogo className="w-10 h-10 text-naqsh-primary dark:text-naqsh-accent" />
                <div>
                  <h1 className="text-lg font-bold text-naqsh-primary dark:text-naqsh-accent">{t("title")}</h1>
                  <p className="text-xs text-gray-500 dark:text-gray-400">{t("subtitle")}</p>
                </div>
              </div>

              {step === "login" ? (
                <form onSubmit={handleLogin} className="space-y-5">
                  <div>
                    <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{t("login")}</h2>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{t("loginHint")}</p>
                  </div>
                  <div className="space-y-4">
                    <div>
                      <label htmlFor="username" className="block text-xs font-semibold uppercase tracking-wide text-gray-600 dark:text-gray-400 mb-1.5">
                        {t("username")}
                      </label>
                      <input
                        id="username"
                        type="text"
                        autoComplete="username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        className={inputClass}
                        required
                      />
                    </div>
                    <div>
                      <label htmlFor="password" className="block text-xs font-semibold uppercase tracking-wide text-gray-600 dark:text-gray-400 mb-1.5">
                        {t("password")}
                      </label>
                      <input
                        id="password"
                        type="password"
                        autoComplete="current-password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className={inputClass}
                        required
                      />
                    </div>
                  </div>
                  {error && (
                    <p className="text-sm text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900/50 rounded-lg px-3 py-2" role="alert">
                      {error}
                    </p>
                  )}
                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full py-3 bg-naqsh-primary text-white rounded-lg font-semibold text-sm hover:bg-[#163328] dark:hover:bg-naqsh-primary/90 disabled:opacity-50 transition-colors shadow-sm"
                  >
                    {loading ? "…" : t("login")}
                  </button>
                </form>
              ) : step === "mfa_setup" && setupToken ? (
                <MfaSetupForm
                  setupToken={setupToken}
                  onComplete={(accessToken) => {
                    if (accessToken) {
                      localStorage.setItem("tmb_access_token", accessToken);
                      setAuthCookie(accessToken);
                      window.location.href = homePathForRole(getRoleFromToken(accessToken));
                    }
                  }}
                  onError={(code) => handleError(code)}
                />
              ) : (
                <form onSubmit={handleMfa} className="space-y-5">
                  <h2 className="font-semibold text-naqsh-primary dark:text-naqsh-accent">{t("mfaTitle")}</h2>
                  <div>
                    <label htmlFor="mfa" className="block text-xs font-semibold uppercase tracking-wide text-gray-600 dark:text-gray-400 mb-1.5">
                      {t("mfaCode")}
                    </label>
                    <input
                      id="mfa"
                      type="text"
                      inputMode="numeric"
                      autoComplete="one-time-code"
                      value={mfaCode}
                      onChange={(e) => setMfaCode(e.target.value)}
                      className={`${inputClass} tracking-[0.3em] text-center text-lg`}
                      required
                    />
                  </div>
                  {error && (
                    <p className="text-sm text-red-600 dark:text-red-400" role="alert">
                      {error}
                    </p>
                  )}
                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full py-3 bg-naqsh-accent text-gray-900 rounded-lg font-semibold text-sm hover:brightness-105 disabled:opacity-50 transition-all"
                  >
                    {t("verify")}
                  </button>
                </form>
              )}

              <p className="text-center mt-6 pt-4 border-t border-gray-100 dark:border-gray-800 text-sm text-gray-500 dark:text-gray-400">
                <a href="/parent/login" className="text-naqsh-accent hover:underline font-medium">
                  {t("parentPortal")}
                </a>
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
