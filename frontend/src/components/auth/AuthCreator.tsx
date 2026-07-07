"use client";

import { useTranslations } from "next-intl";

const CREATOR_IMAGE = "/images/kamolbek-creator.png?v=original";

export function AuthCreator() {
  const t = useTranslations("auth.landing.creator");

  return (
    <section className="aeline-creator aeline-section" aria-label={t("ariaLabel")}>
      <div className="aeline-container aeline-creator__grid">
        <div className="aeline-creator__content">
          <div className="aeline-tag">
            <span className="aeline-tag__dot" />
            {t("tag")}
          </div>
          <h2 className="aeline-creator__title">{t("title")}</h2>
          <p className="aeline-creator__desc">{t("desc")}</p>
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
        </div>
        <div className="aeline-creator__visual">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={CREATOR_IMAGE}
            alt={t("imageAlt")}
            className="aeline-creator__image"
            loading="lazy"
            width={1024}
            height={1024}
          />
        </div>
      </div>
    </section>
  );
}
