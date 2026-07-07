"use client";

import { useTranslations } from "next-intl";
import { AuthHero3D } from "@/components/auth/AuthHero3D";
import { AuthHeroActions, AuthHeroRating, AuthNavbar } from "@/components/auth/AuthNavbar";
import { AuthLandingSections } from "@/components/auth/AuthLandingSections";
import { AuthSplitLoginCard } from "@/components/auth/AuthSplitLoginCard";

export function AuthChrome({
  children,
  alternateHref,
  alternateLabel,
  heroTitle,
  heroSubtitle,
  welcomeTitle,
  welcomeSubtitle,
}: {
  children: React.ReactNode;
  alternateHref?: string;
  alternateLabel?: string;
  heroTitle?: string;
  heroSubtitle?: string;
  welcomeTitle?: string;
  welcomeSubtitle?: string;
}) {
  const t = useTranslations("auth");
  const landing = useTranslations("auth.landing");

  return (
    <div className="auth-aeline">
      <AuthNavbar />

      <section className="aeline-hero">
        <div className="aeline-hero__content">
          <div className="aeline-container aeline-hero__text">
            <h1 className="aeline-hero__title">
              {heroTitle || landing("hero.title")}
              <span className="aeline-hero__title-muted"> {landing("hero.titleAccent")}</span>
            </h1>
            <p className="aeline-hero__subtitle">{heroSubtitle || landing("hero.subtitle")}</p>
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
            <AuthSplitLoginCard
              welcomeTitle={welcomeTitle || t("splitWelcomeTitle")}
              welcomeSubtitle={welcomeSubtitle || t("splitWelcomeSubtitle")}
              sideHref={alternateHref}
              sideLabel={alternateLabel}
            >
              {children}
            </AuthSplitLoginCard>
          </div>
        </div>
      </section>

      <AuthLandingSections />
    </div>
  );
}
