"use client";

import Link from "next/link";
import { useTranslations } from "next-intl";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { ThemeToggle } from "@/components/ThemeToggle";
import { TmbLogo } from "@/components/TmbLogo";

export function AuthChrome({
  children,
  alternateHref,
  alternateLabel,
}: {
  children: React.ReactNode;
  alternateHref?: string;
  alternateLabel?: string;
}) {
  const t = useTranslations("auth");

  return (
    <div className="min-h-screen auth-hero-bg flex flex-col text-white relative">
      <header className="relative z-10 flex justify-between items-center gap-3 px-4 sm:px-6 py-4">
        <div className="flex items-center gap-2.5">
          <TmbLogo className="w-9 h-9 text-naqsh-accent" />
          <div className="hidden sm:block">
            <div className="font-semibold text-sm tracking-wide">TMB</div>
            <div className="text-[11px] text-white/60">{t("footer.region")}</div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <ThemeToggle />
          <LanguageSwitcher />
        </div>
      </header>

      <main className="relative z-10 flex-1 flex items-center justify-center px-4 py-6 sm:py-10">
        <div className="w-full max-w-md">
          <div className="glass-card rounded-2xl px-7 sm:px-8 py-8 sm:py-9 text-center">
            {children}
          </div>
          {alternateHref && alternateLabel && (
            <p className="text-center mt-5 text-sm text-white/70">
              <Link href={alternateHref} className="text-naqsh-accent hover:underline font-medium">
                {alternateLabel}
              </Link>
            </p>
          )}
        </div>
      </main>

      <footer className="relative z-10 py-6 sm:py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-[1fr_auto_1fr] items-center gap-4 text-sm">
            <div className="flex flex-wrap justify-center md:justify-end gap-x-5 gap-y-2 order-2 md:order-1">
              <Link href="/verify" className="text-white/75 hover:text-white hover:underline transition-colors">
                {t("footer.verify")}
              </Link>
              <span className="hidden sm:inline text-white/30">·</span>
              <span className="text-white/55 text-xs sm:text-sm">{t("footer.platform")}</span>
            </div>
            <div className="flex justify-center order-1 md:order-2">
              <div className="p-2.5 rounded-xl bg-white/10 border border-white/20">
                <TmbLogo className="w-8 h-8 text-naqsh-accent" />
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
