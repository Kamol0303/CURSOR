"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTranslations } from "next-intl";
import { AuthButton } from "@/components/AuthButton";
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
  const pathname = usePathname();
  const isParent = pathname?.startsWith("/parent");

  return (
    <div className="auth-agentflow min-h-screen flex flex-col relative overflow-hidden">
      <div className="auth-agentflow__dots" aria-hidden />

      <header className="auth-agentflow-header auth-animate-in">
        <Link href="/" className="auth-agentflow-header__brand">
          <TmbLogo className="auth-agentflow-header__logo" />
          <div className="min-w-0">
            <div className="auth-agentflow-header__title">TMB</div>
            <div className="auth-agentflow-header__subtitle">{t("footer.region")}</div>
          </div>
        </Link>

        <nav className="auth-agentflow-nav" aria-label="Auth navigation">
          <Link href="/" className={`auth-agentflow-nav__link ${!isParent ? "is-active" : ""}`}>
            {t("footer.staff")}
          </Link>
          <Link href="/parent/login" className={`auth-agentflow-nav__link ${isParent ? "is-active" : ""}`}>
            {t("footer.parent")}
          </Link>
          <Link href="/verify" className="auth-agentflow-nav__link">
            {t("footer.verify")}
          </Link>
        </nav>

        <div className="auth-agentflow-header__actions">
          <ThemeToggle />
          <LanguageSwitcher />
          <span className="hidden sm:inline-flex auth-af-btn-border--compact">
            <AuthButton
              variant="primary"
              fullWidth={false}
              type="button"
              onClick={() => {
                window.location.href = isParent ? "/" : "/parent/login";
              }}
            >
              {isParent ? t("footer.staff") : t("footer.parent")}
            </AuthButton>
          </span>
        </div>
      </header>

      <main className="auth-agentflow-main">
        <div className="auth-agentflow-grid">
          {(heroTitle || heroSubtitle) && (
            <div className="auth-agentflow-hero auth-animate-in" style={{ animationDelay: "0.08s" }}>
              <div className="auth-agentflow-hero__eyebrow">tmb.monitoring · v1</div>
              {heroTitle && <h1 className="auth-agentflow-hero__title">{heroTitle}</h1>}
              {heroSubtitle && <p className="auth-agentflow-hero__subtitle">{heroSubtitle}</p>}
              <div className="auth-agentflow-hero__stats">
                <div className="auth-agentflow-stat">
                  <div className="auth-agentflow-stat__value">20+</div>
                  <div className="auth-agentflow-stat__label">{t("heroStats.modules")}</div>
                </div>
                <div className="auth-agentflow-stat">
                  <div className="auth-agentflow-stat__value">RBAC</div>
                  <div className="auth-agentflow-stat__label">{t("heroStats.security")}</div>
                </div>
                <div className="auth-agentflow-stat">
                  <div className="auth-agentflow-stat__value">24/7</div>
                  <div className="auth-agentflow-stat__label">{t("heroStats.monitoring")}</div>
                </div>
              </div>
            </div>
          )}

          <div className="auth-animate-in" style={{ animationDelay: "0.16s" }}>
            <div className="auth-agentflow-card">
              <div className="auth-agentflow-card__mobile-logo">
                <div className="auth-agentflow-card__logo-wrap">
                  <TmbLogo className="w-9 h-9" />
                </div>
              </div>
              {children}
            </div>
            {alternateHref && alternateLabel && (
              <p className="auth-agentflow-alt">
                <Link href={alternateHref}>{alternateLabel}</Link>
              </p>
            )}
          </div>
        </div>
      </main>

      <footer className="auth-agentflow-footer auth-animate-in" style={{ animationDelay: "0.24s" }}>
        <div className="auth-agentflow-footer__glow" aria-hidden />
        <div className="auth-agentflow-footer__inner">
          <div className="auth-agentflow-footer__top">
            <div className="auth-agentflow-footer__brand">
              <Link href="/" className="inline-flex items-center gap-2.5">
                <TmbLogo className="w-9 h-9 text-sky-400" />
                <span className="font-semibold text-white text-lg tracking-wide">TMB</span>
              </Link>
              <p>{t("subtitle")}</p>
              <div className="auth-agentflow-footer__badge">$ tmb login --region toyloq</div>
            </div>
            <div className="auth-agentflow-footer__columns">
              <div>
                <div className="auth-agentflow-footer__heading">{t("footer.platform")}</div>
                <div className="auth-agentflow-footer__list">
                  <Link href="/">{t("footer.staff")}</Link>
                  <Link href="/parent/login">{t("footer.parent")}</Link>
                  <Link href="/verify">{t("footer.verify")}</Link>
                </div>
              </div>
              <div>
                <div className="auth-agentflow-footer__heading">{t("footer.region")}</div>
                <div className="auth-agentflow-footer__list">
                  <span>{t("heroStats.monitoring")}</span>
                  <span>RBAC · MFA</span>
                  <span>{t("footer.copyright")}</span>
                </div>
              </div>
            </div>
          </div>
          <div className="auth-agentflow-footer__bottom">
            <div>{t("footer.copyright")}</div>
            <div>{t("footer.region")}</div>
          </div>
        </div>
      </footer>
    </div>
  );
}
