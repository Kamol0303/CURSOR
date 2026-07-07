"use client";

import { useState } from "react";
import Link from "next/link";
import { useTranslations } from "next-intl";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { ThemeToggle } from "@/components/ThemeToggle";
import { MfaSetupForm } from "@/components/MfaSetupForm";
import { TmbLogo } from "@/components/TmbLogo";
import { Alert, BezelCard, Button, FormField, Input, Label } from "@/components/ui";
import { getApiBaseUrl } from "@/lib/api";
import { getRoleFromToken, homePathForRole, setAuthCookie } from "@/lib/auth-cookie";

type Step = "login" | "mfa" | "mfa_setup";

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
          <span className="font-semibold text-small tracking-wide hidden sm:inline">TMB</span>
        </div>
        <div className="flex items-center gap-2">
          <ThemeToggle />
          <LanguageSwitcher />
        </div>
      </header>

      <main className="flex-1 flex items-center justify-center p-4 sm:p-6">
        <div className="w-full max-w-4xl animate-slide-up">
          <BezelCard padding="p-2" className="overflow-hidden">
            <div className="grid lg:grid-cols-[1fr_1.1fr] overflow-hidden rounded-[calc(1rem-0.25rem)]">
            <div className="hidden lg:flex flex-col justify-between bg-gradient-to-br from-[#1b4d3e] via-[#1e3a2f] to-[#122a22] text-white p-10 relative overflow-hidden">
              <div className="absolute inset-0 opacity-[0.07] girih-bg pointer-events-none" aria-hidden />
              <div className="relative">
                <TmbLogo className="w-14 h-14 text-naqsh-accent mb-6" />
                <h1 className="text-h2 text-white mb-3">{t("title")}</h1>
                <p className="text-small text-white/75 leading-relaxed max-w-xs">{t("subtitle")}</p>
              </div>
              <p className="relative text-caption text-white/50 border-t border-white/10 pt-4">
                Toyloq tumani · Samarqand viloyati
              </p>
            </div>

            <div className="p-6 sm:p-8 lg:p-10 flex flex-col justify-center border-t-4 border-naqsh-accent lg:border-t-0 lg:border-l-4">
              <div className="lg:hidden flex items-center gap-3 mb-6">
                <TmbLogo className="w-10 h-10 text-naqsh-primary dark:text-naqsh-accent" />
                <div>
                  <h1 className="text-h3 text-naqsh-primary dark:text-naqsh-accent">{t("title")}</h1>
                  <p className="text-caption text-muted-foreground">{t("subtitle")}</p>
                </div>
              </div>

              {step === "login" ? (
                <form onSubmit={handleLogin} className="space-y-5">
                  <div>
                    <h2 className="text-h3 text-foreground">{t("login")}</h2>
                    <p className="text-caption text-muted-foreground mt-1">{t("loginHint")}</p>
                  </div>
                  <div className="space-y-4">
                    <FormField>
                      <Label htmlFor="username">{t("username")}</Label>
                      <Input
                        id="username"
                        type="text"
                        autoComplete="username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                      />
                    </FormField>
                    <FormField>
                      <Label htmlFor="password">{t("password")}</Label>
                      <Input
                        id="password"
                        type="password"
                        autoComplete="current-password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                      />
                    </FormField>
                  </div>
                  {error && <Alert variant="danger">{error}</Alert>}
                  <Button type="submit" loading={loading} className="w-full" size="lg">
                    {t("login")}
                  </Button>
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
                  <h2 className="text-h3 text-naqsh-primary dark:text-naqsh-accent">{t("mfaTitle")}</h2>
                  <FormField>
                    <Label htmlFor="mfa">{t("mfaCode")}</Label>
                    <Input
                      id="mfa"
                      type="text"
                      inputMode="numeric"
                      autoComplete="one-time-code"
                      value={mfaCode}
                      onChange={(e) => setMfaCode(e.target.value)}
                      className="tracking-[0.3em] text-center text-lg"
                      required
                    />
                  </FormField>
                  {error && <Alert variant="danger">{error}</Alert>}
                  <Button type="submit" variant="accent" loading={loading} className="w-full" size="lg">
                    {t("verify")}
                  </Button>
                </form>
              )}

              <p className="text-center mt-6 pt-4 border-t border-border text-small text-muted-foreground">
                <Link href="/parent/login" className="text-naqsh-accent hover:underline font-medium transition-colors">
                  {t("parentPortal")}
                </Link>
              </p>
            </div>
            </div>
          </BezelCard>
        </div>
      </main>
    </div>
  );
}
