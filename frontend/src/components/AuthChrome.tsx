"use client";

import Link from "next/link";
import { useTranslations } from "next-intl";
import { AuthHero3D } from "@/components/auth/AuthHero3D";
import { AuthHeroActions, AuthHeroRating, AuthNavbar } from "@/components/auth/AuthNavbar";
import { AuthLandingSections } from "@/components/auth/AuthLandingSections";

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
  const t = useTranslations("auth.landing");

  return (
    <div className="auth-aeline">
      <AuthNavbar />

      <section className="aeline-hero">
        <div className="aeline-hero__content">
          <div className="aeline-container aeline-hero__text">
            <h1 className="aeline-hero__title">
              {heroTitle || t("hero.title")}
              <span className="aeline-hero__title-muted"> {t("hero.titleAccent")}</span>
            </h1>
            <p className="aeline-hero__subtitle">{heroSubtitle || t("hero.subtitle")}</p>
            <AuthHeroActions />
          </div>

          <div className="aeline-hero__stage">
            <AuthHero3D />
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="https://images.unsplash.com/photo-1509062522246-3755977927d7?w=1920&q=80"
              alt=""
              className="aeline-hero__bg"
              loading="eager"
            />
            <AuthHeroRating />
          </div>

          <div className="aeline-container aeline-hero__login-col">
            <div id="login" className="aeline-login-card">
              {children}
              {alternateHref && alternateLabel && (
                <p className="aeline-login-card__alt">
                  <Link href={alternateHref}>{alternateLabel}</Link>
                </p>
              )}
            </div>
          </div>
        </div>
      </section>

      <AuthLandingSections />
    </div>
  );
}
