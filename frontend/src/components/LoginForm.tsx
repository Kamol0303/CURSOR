"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { AuthChrome } from "@/components/AuthChrome";
import { GlassInput } from "@/components/GlassInput";
import { GridGlowEffect } from "@/components/GridGlowEffect";
import { MfaSetupForm } from "@/components/MfaSetupForm";
import { TmbLogo } from "@/components/TmbLogo";

import { getApiBaseUrl } from "@/lib/api";
import { getRoleFromToken, homePathForRole, setAuthCookie } from "@/lib/auth-cookie";

type Step = "login" | "mfa" | "mfa_setup";

const REMEMBER_KEY = "tmb_remember_username";

const glassBtn =
  "w-full bg-white text-gray-900 font-semibold py-3 rounded-md border-2 border-transparent hover:text-white hover:border-white hover:bg-white/15 transition-all duration-300 disabled:opacity-50 text-base";

export function LoginForm() {
  const t = useTranslations("auth");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(false);
  const [step, setStep] = useState<Step>("login");
  const [mfaToken, setMfaToken] = useState<string | null>(null);
  const [setupToken, setSetupToken] = useState<string | null>(null);
  const [mfaCode, setMfaCode] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [showForgotHint, setShowForgotHint] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem(REMEMBER_KEY);
    if (saved) {
      setUsername(saved);
      setRemember(true);
    }
  }, []);

  const handleError = (code: string) => {
    const key = `errors.${code}` as "errors.INVALID_CREDENTIALS";
    try {
      setError(t(key));
    } catch {
      setError(code);
    }
  };

  const persistRemember = (name: string) => {
    if (remember) {
      localStorage.setItem(REMEMBER_KEY, name);
    } else {
      localStorage.removeItem(REMEMBER_KEY);
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
      persistRemember(username.trim());
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
    <AuthChrome
      alternateHref="/parent/login"
      alternateLabel={t("parentPortal")}
      heroTitle={t("title")}
      heroSubtitle={t("subtitle")}
    >
      {step === "login" ? (
        <form onSubmit={handleLogin} className="text-left flex flex-col">
          <div className="flex justify-center mb-5 lg:hidden">
            <div className="relative w-16 h-16 rounded-2xl overflow-hidden border border-white/20">
              <GridGlowEffect className="inset-0" columns={6} rows={6} compact color="#c8932a" />
              <div className="absolute inset-0 flex items-center justify-center z-10 pointer-events-none">
                <TmbLogo className="w-9 h-9 text-naqsh-accent auth-logo-float" />
              </div>
            </div>
          </div>

          <h2 className="text-2xl font-semibold text-white text-center mb-1">{t("login")}</h2>
          <p className="text-xs text-white/60 text-center mb-6">{t("loginHint")}</p>

          <GlassInput
            label={t("username")}
            value={username}
            onChange={setUsername}
            autoComplete="username"
            id="username"
          />
          <GlassInput
            label={t("password")}
            type="password"
            value={password}
            onChange={setPassword}
            autoComplete="current-password"
            id="password"
            className="mt-4"
          />

          <div className="flex items-center justify-between mt-6 mb-7 text-sm text-white/85">
            <label htmlFor="remember" className="flex items-center gap-2 cursor-pointer select-none">
              <input
                id="remember"
                type="checkbox"
                checked={remember}
                onChange={(e) => setRemember(e.target.checked)}
                className="accent-naqsh-accent w-4 h-4 rounded"
              />
              <span>{t("rememberMe")}</span>
            </label>
            <button
              type="button"
              onClick={() => setShowForgotHint((v) => !v)}
              className="text-white/80 hover:text-white hover:underline transition-colors"
            >
              {t("forgotPassword")}
            </button>
          </div>

          {showForgotHint && (
            <p className="text-xs text-white/65 bg-white/5 border border-white/10 rounded-lg px-3 py-2 mb-4 -mt-3">
              {t("forgotPasswordHint")}
            </p>
          )}

          {error && (
            <p
              className="text-sm text-red-200 bg-red-500/15 border border-red-400/30 rounded-lg px-3 py-2 mb-4"
              role="alert"
            >
              {error}
            </p>
          )}

          <button type="submit" disabled={loading} className={glassBtn}>
            {loading ? "…" : t("login")}
          </button>

          <p className="text-center mt-6 text-sm text-white/60">{t("subtitle")}</p>
        </form>
      ) : step === "mfa_setup" && setupToken ? (
        <div className="text-left">
          <MfaSetupForm
            variant="glass"
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
          {error && (
            <p className="text-sm text-red-200 mt-3" role="alert">
              {error}
            </p>
          )}
        </div>
      ) : (
        <form onSubmit={handleMfa} className="text-left flex flex-col">
          <h2 className="text-xl font-semibold text-white text-center mb-6">{t("mfaTitle")}</h2>
          <GlassInput
            label={t("mfaCode")}
            value={mfaCode}
            onChange={setMfaCode}
            inputMode="numeric"
            autoComplete="one-time-code"
            id="mfa"
            className="[&_input]:tracking-[0.3em] [&_input]:text-center [&_input]:text-lg"
          />
          {error && (
            <p className="text-sm text-red-200 mt-4" role="alert">
              {error}
            </p>
          )}
          <button type="submit" disabled={loading} className={`${glassBtn} mt-7`}>
            {t("verify")}
          </button>
        </form>
      )}
    </AuthChrome>
  );
}
