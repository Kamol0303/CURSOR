"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function LoginForm() {
  const t = useTranslations("auth");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [mfaToken, setMfaToken] = useState<string | null>(null);
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
      const res = await fetch(`${API_URL}/api/v1/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ username, password }),
      });
      const data = await res.json();
      if (!res.ok) {
        handleError(data.detail?.code || "INVALID_CREDENTIALS");
        return;
      }
      if (data.data?.requires_mfa) {
        setMfaToken(data.data.mfa_token);
        return;
      }
      localStorage.setItem("tamor_access_token", data.data.access_token);
      window.location.href = "/dashboard";
    } catch {
      setError(t("errors.INVALID_CREDENTIALS"));
    } finally {
      setLoading(false);
    }
  };

  const handleMfa = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/api/v1/auth/mfa/verify`, {
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
      localStorage.setItem("tamor_access_token", data.data.access_token);
      window.location.href = "/dashboard";
    } catch {
      setError(t("errors.MFA_INVALID"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen girih-bg flex flex-col">
      <header className="flex justify-end p-4">
        <LanguageSwitcher />
      </header>
      <main className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-md bg-white/95 dark:bg-gray-900/95 backdrop-blur rounded-2xl shadow-xl border border-naqsh-primary/10 p-8">
          <div className="flex items-center gap-3 mb-6">
            <svg viewBox="0 0 48 48" className="w-12 h-12 text-naqsh-primary" aria-hidden="true">
              <path
                d="M24 4 L24 14 M24 34 L24 44 M4 24 L14 24 M34 24 L44 24 M24 14 L34 24 L24 34 L14 24 Z"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              />
            </svg>
            <div>
              <h1 className="text-xl font-bold text-naqsh-primary">{t("title")}</h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">{t("subtitle")}</p>
            </div>
          </div>

          {!mfaToken ? (
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label htmlFor="username" className="block text-sm font-medium mb-1">
                  {t("username")}
                </label>
                <input
                  id="username"
                  type="text"
                  autoComplete="username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-naqsh-primary/30 focus:border-naqsh-primary outline-none"
                  required
                />
              </div>
              <div>
                <label htmlFor="password" className="block text-sm font-medium mb-1">
                  {t("password")}
                </label>
                <input
                  id="password"
                  type="password"
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-naqsh-primary/30 focus:border-naqsh-primary outline-none"
                  required
                />
              </div>
              {error && (
                <p className="text-sm text-red-600" role="alert">
                  {error}
                </p>
              )}
              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 bg-naqsh-primary text-white rounded-lg font-medium hover:bg-naqsh-primary/90 disabled:opacity-50 transition-colors"
              >
                {t("login")}
              </button>
            </form>
          ) : (
            <form onSubmit={handleMfa} className="space-y-4">
              <h2 className="font-semibold text-naqsh-primary">{t("mfaTitle")}</h2>
              <div>
                <label htmlFor="mfa" className="block text-sm font-medium mb-1">
                  {t("mfaCode")}
                </label>
                <input
                  id="mfa"
                  type="text"
                  inputMode="numeric"
                  autoComplete="one-time-code"
                  value={mfaCode}
                  onChange={(e) => setMfaCode(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-naqsh-primary/30 focus:border-naqsh-primary outline-none tracking-widest text-center"
                  required
                />
              </div>
              {error && (
                <p className="text-sm text-red-600" role="alert">
                  {error}
                </p>
              )}
              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 bg-naqsh-accent text-white rounded-lg font-medium hover:opacity-90 disabled:opacity-50 transition-colors"
              >
                {t("verify")}
              </button>
            </form>
          )}
        </div>
        <p className="text-center mt-4 text-sm text-gray-600">
          <a href="/parent/login" className="text-naqsh-accent hover:underline">
            Ota-ona portali →
          </a>
        </p>
      </main>
    </div>
  );
}
