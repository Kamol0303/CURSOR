"use client";

import { useTranslations } from "next-intl";

export function AuthCreator() {
  const t = useTranslations("auth.landing.creator");

  return (
    <section className="aeline-creator" aria-label={t("ariaLabel")}>
      <div className="aeline-creator__card">
        <div className="aeline-creator__avatar">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/images/kamolbek-creator.png" alt={t("name")} loading="lazy" />
        </div>
        <div className="aeline-creator__text">
          <span className="aeline-creator__label">{t("label")}</span>
          <span className="aeline-creator__name">{t("name")}</span>
        </div>
        <a href="#" className="aeline-creator__link" aria-label={t("linkAria")}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden>
            <path d="M7 17L17 7M17 7H7M17 7V17" />
          </svg>
        </a>
      </div>
    </section>
  );
}
