"use client";

import Link from "next/link";
import { useTranslations } from "next-intl";
import { GridGlowEffect } from "@/components/GridGlowEffect";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { ThemeToggle } from "@/components/ThemeToggle";
import { TmbLogo } from "@/components/TmbLogo";

export function AuthChrome({
  children,
  alternateHref,
  alternateLabel,
  heroTitle,
  heroSubtitle,
}: {
  children: React.ReactNode;
  alternateHref?: string;
  alternateLabel?: string;
  heroTitle?: string;
  heroSubtitle?: string;
}) {
  const t = useTranslations("auth");

  return (
    <div className="min-h-screen auth-hero-bg flex flex-col text-white relative overflow-hidden">
      <div className="auth-orb auth-orb-1" aria-hidden />
      <div className="auth-orb auth-orb-2" aria-hidden />

      <GridGlowEffect className="fixed inset-0 opacity-50 pointer-events-auto" color="#c8932a" />

      <header className="relative z-20 flex justify-between items-center gap-3 px-4 sm:px-6 py-4 sm:py-5 auth-animate-in">
        <div className="flex items-center gap-3 sm:gap-3.5 min-w-0">
          <TmbLogo className="w-11 h-11 sm:w-12 sm:h-12 shrink-0 text-naqsh-accent auth-logo-float" />
          <div className="auth-brand min-w-0">
            <div className="auth-brand__title">TMB</div>
            <div className="auth-brand__region truncate">{t("footer.region")}</div>
          </div>
        </div>
        <div className="flex items-center gap-2 pointer-events-auto">
          <ThemeToggle />
          <LanguageSwitcher />
        </div>
      </header>

      <main className="relative z-20 flex-1 flex items-center justify-center px-4 py-6 sm:py-8 pointer-events-none">
        <div className="w-full max-w-5xl grid lg:grid-cols-[1fr_1.05fr] gap-6 lg:gap-8 items-center">
          {(heroTitle || heroSubtitle) && (
            <div className="hidden lg:block auth-animate-in" style={{ animationDelay: "0.1s" }}>
              <div className="grid-hero-card aspect-square max-h-[28rem] mx-auto w-full pointer-events-auto">
                <GridGlowEffect className="inset-0" color="#c8932a" />
                <div className="relative z-10 h-full flex flex-col items-center justify-center p-10 text-center pointer-events-none">
                  <TmbLogo className="w-20 h-20 text-naqsh-accent auth-logo-float mb-8" />
                  {heroTitle && (
                    <h1 className="text-2xl font-bold leading-snug mb-3 max-w-xs">{heroTitle}</h1>
                  )}
                  {heroSubtitle && (
                    <p className="text-sm text-white/70 leading-relaxed max-w-sm">{heroSubtitle}</p>
                  )}
                  <p className="mt-8 text-xs text-white/45 border-t border-white/10 pt-4 w-full">
                    {t("footer.region")}
                  </p>
                </div>
              </div>
            </div>
          )}

          <div
            className="w-full max-w-md mx-auto lg:max-w-none auth-animate-in pointer-events-auto"
            style={{ animationDelay: "0.2s" }}
          >
            <div className="relative">
              <div className="absolute -inset-3 rounded-3xl overflow-hidden opacity-40 pointer-events-auto hidden sm:block">
                <GridGlowEffect className="inset-0" columns={8} rows={8} compact color="#c8932a" />
              </div>
              <div className="glass-card rounded-2xl px-7 sm:px-8 py-8 sm:py-9 text-center relative z-10">
                {children}
              </div>
            </div>
            {alternateHref && alternateLabel && (
              <p className="text-center mt-5 text-sm text-white/70">
                <Link href={alternateHref} className="text-naqsh-accent hover:underline font-medium">
                  {alternateLabel}
                </Link>
              </p>
            )}
          </div>
        </div>
      </main>

      <footer className="relative z-20 py-6 sm:py-8 auth-animate-in pointer-events-none" style={{ animationDelay: "0.35s" }}>
        <div className="max-w-4xl mx-auto px-4 pointer-events-auto">
          <div className="grid grid-cols-1 md:grid-cols-[1fr_auto_1fr] items-center gap-4 text-sm">
            <div className="flex flex-wrap justify-center md:justify-end gap-x-5 gap-y-2 order-2 md:order-1">
              <Link href="/verify" className="text-white/75 hover:text-white hover:underline transition-colors">
                {t("footer.verify")}
              </Link>
              <span className="hidden sm:inline text-white/30">·</span>
              <span className="text-white/55 text-xs sm:text-sm">{t("footer.platform")}</span>
            </div>
            <div className="flex justify-center order-1 md:order-2">
              <div className="relative p-2.5 rounded-xl bg-white/10 border border-white/20 overflow-hidden">
                <GridGlowEffect className="inset-0" columns={6} rows={6} compact color="#c8932a" />
                <TmbLogo className="w-8 h-8 text-naqsh-accent relative z-10 pointer-events-none" />
              </div>
            </div>
            <div className="flex flex-wrap justify-center md:justify-start gap-x-5 gap-y-2 order-3">
              <Link href="/parent/login" className="text-white/75 hover:text-white hover:underline transition-colors">
                {t("footer.parent")}
              </Link>
              <span className="hidden sm:inline text-white/30">·</span>
              <Link href="/" className="text-white/75 hover:text-white hover:underline transition-colors">
                {t("footer.staff")}
              </Link>
            </div>
          </div>
          <p className="text-center text-[11px] text-white/40 mt-4">{t("footer.copyright")}</p>
        </div>
      </footer>
    </div>
  );
}
