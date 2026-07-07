"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { AuthButton } from "@/components/AuthButton";
import { AuthChrome } from "@/components/AuthChrome";
import { GlassInput } from "@/components/GlassInput";
import { MfaSetupForm } from "@/components/MfaSetupForm";

import { getApiBaseUrl } from "@/lib/api";
import { getRoleFromToken, homePathForRole, setAuthCookie } from "@/lib/auth-cookie";

type Step = "login" | "mfa" | "mfa_setup";

const REMEMBER_KEY = "tmb_remember_username";

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
          <h2 className="aeline-login-card__title">{t("login")}</h2>
          <p className="aeline-login-card__hint">{t("loginHint")}</p>

          <GlassInput
            label={t("username")}
            value={username}
            onChange={setUsername}
            autoComplete="username"
            id="username"
            variant="light"
          />
          <GlassInput
            label={t("password")}
            type="password"
            value={password}
            onChange={setPassword}
            autoComplete="current-password"
            id="password"
            className="mt-4"
            variant="light"
          />

          <div className="flex items-center justify-between mt-6 mb-6 text-sm text-slate-600">
            <label htmlFor="remember" className="flex items-center gap-2 cursor-pointer select-none">
              <input
                id="remember"
                type="checkbox"
                checked={remember}
                onChange={(e) => setRemember(e.target.checked)}
                className="accent-blue-600 w-4 h-4 rounded"
              />
              <span>{t("rememberMe")}</span>
            </label>
            <button
              type="button"
              onClick={() => setShowForgotHint((v) => !v)}
              className="text-slate-600 hover:text-blue-600 hover:underline transition-colors"
            >
              {t("forgotPassword")}
            </button>
          </div>

          {showForgotHint && (
            <p className="aeline-alert aeline-alert--info -mt-2 mb-4">{t("forgotPasswordHint")}</p>
          )}

          {error && (
            <p className="aeline-alert aeline-alert--error" role="alert">
              {error}
            </p>
          )}

          <AuthButton type="submit" disabled={loading}>
            {loading ? "…" : t("login")}
          </AuthButton>
        </form>
      ) : step === "mfa_setup" && setupToken ? (
        <div className="text-left">
          <MfaSetupForm
            variant="light"
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
            <p className="aeline-alert aeline-alert--error mt-3" role="alert">
              {error}
            </p>
          )}
        </div>
      ) : (
        <form onSubmit={handleMfa} className="text-left flex flex-col">
          <h2 className="aeline-login-card__title">{t("mfaTitle")}</h2>
          <p className="aeline-login-card__hint">{t("mfaCode")}</p>
          <GlassInput
            label={t("mfaCode")}
            value={mfaCode}
            onChange={setMfaCode}
            inputMode="numeric"
            autoComplete="one-time-code"
            id="mfa"
            variant="light"
            className="[&_input]:tracking-[0.3em] [&_input]:text-center [&_input]:text-lg"
          />
          {error && (
            <p className="aeline-alert aeline-alert--error mt-4" role="alert">
              {error}
            </p>
          )}
          <div className="mt-7">
            <AuthButton type="submit" disabled={loading}>
              {t("verify")}
            </AuthButton>
          </div>
        </form>
      )}
    </AuthChrome>
  );
}
