"use client";

import Link from "next/link";
import { useTranslations } from "next-intl";
import { AuthArrowButton } from "@/components/AuthButton";
import { TmbLogo } from "@/components/TmbLogo";

const PARTNER_LABELS = ["Toyloq tumani", "Samarqand", "Markazlar", "O'quvchilar", "O'qituvchilar", "Monitoring"];

const SERVICE_IMAGES = [
  "https://images.unsplash.com/photo-1552664730-d307ca884978?w=800&q=80",
  "https://images.unsplash.com/photo-1434030216561-bbafb2e79fd4?w=800&q=80",
  "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&q=80",
];

const TESTIMONIAL_IMAGES = [
  "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=600&q=80",
  "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=600&q=80",
  "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=600&q=80",
];

export function AuthLandingSections() {
  const t = useTranslations("auth.landing");

  return (
    <>
      <section className="aeline-loop" aria-label="Partners">
        <div className="aeline-loop__track">
          {[...PARTNER_LABELS, ...PARTNER_LABELS].map((label, i) => (
            <span key={`${label}-${i}`} className="aeline-loop__item">
              {label}
            </span>
          ))}
        </div>
        <div className="aeline-loop__track aeline-loop__track--reverse" aria-hidden>
          {[...PARTNER_LABELS, ...PARTNER_LABELS].map((label, i) => (
            <span key={`r-${label}-${i}`} className="aeline-loop__item">
              {label}
            </span>
          ))}
        </div>
      </section>

      <section id="about" className="aeline-section">
        <div className="aeline-container">
          <div className="aeline-section__head">
            <div className="aeline-tag">
              <span className="aeline-tag__dot" />
              {t("about.tag")}
            </div>
            <h2 className="aeline-section__title aeline-section__title--split">{t("about.title")}</h2>
          </div>
          <div className="aeline-about-grid">
            <div className="aeline-about-card aeline-about-card--featured">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src="https://images.unsplash.com/photo-1523240795612-9a054b0db644?w=900&q=80"
                alt=""
                className="aeline-about-card__img"
                loading="lazy"
              />
              <div className="aeline-about-card__body">
                <div className="aeline-about-card__stat">
                  <span className="aeline-about-card__stat-num">12+</span>
                  <span className="aeline-about-card__stat-label">{t("about.statCenters")}</span>
                </div>
                <p>{t("about.statCentersDesc")}</p>
              </div>
            </div>
            <div className="aeline-about-card aeline-about-card--muted">
              <div className="aeline-about-card__stat">
                <span className="aeline-about-card__stat-num">100%</span>
                <span className="aeline-about-card__stat-label">{t("about.statCommitment")}</span>
              </div>
              <p className="aeline-about-card__quote">{t("about.quote")}</p>
            </div>
            <div className="aeline-about-card aeline-about-card--lime">
              <div className="aeline-about-card__stat">
                <span className="aeline-about-card__stat-num">5k+</span>
                <span className="aeline-about-card__stat-label">{t("about.statStudents")}</span>
              </div>
              <p>{t("about.statStudentsDesc")}</p>
            </div>
            <div className="aeline-about-card aeline-about-card--dark">
              <div className="aeline-about-card__stat">
                <span className="aeline-about-card__stat-num">20+</span>
                <span className="aeline-about-card__stat-label">{t("about.statModules")}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="services" className="aeline-section">
        <div className="aeline-container aeline-section__head--center">
          <div className="aeline-tag">
            <span className="aeline-tag__dot" />
            {t("services.tag")}
          </div>
          <h2 className="aeline-section__title">{t("services.title")}</h2>
          <p className="aeline-section__desc">{t("services.desc")}</p>
          <AuthArrowButton href="#login">{t("services.cta")}</AuthArrowButton>
        </div>
        <div className="aeline-container aeline-services-grid">
          {(["one", "two", "three"] as const).map((key, i) => (
            <article key={key} className={`aeline-service-card aeline-service-card--${i + 1}`}>
              <div className="aeline-service-card__content">
                <div className="aeline-service-card__icon" />
                <h3>{t(`services.items.${key}.title`)}</h3>
                <p>{t(`services.items.${key}.desc`)}</p>
              </div>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={SERVICE_IMAGES[i]} alt="" className="aeline-service-card__img" loading="lazy" />
            </article>
          ))}
        </div>
      </section>

      <section id="expertise" className="aeline-section">
        <div className="aeline-container aeline-section__head--center">
          <div className="aeline-tag">
            <span className="aeline-tag__dot" />
            {t("expertise.tag")}
          </div>
          <h2 className="aeline-section__title">{t("expertise.title")}</h2>
          <p className="aeline-section__desc">{t("expertise.desc")}</p>
        </div>
        <div className="aeline-container aeline-expertise-grid">
          {(["attendance", "analytics"] as const).map((key) => (
            <article key={key} className="aeline-expertise-card">
              <div className="aeline-expertise-card__visual">
                <div className={`aeline-mock aeline-mock--${key}`}>
                  <div className="aeline-mock__bar" />
                  <div className="aeline-mock__bar aeline-mock__bar--short" />
                  <div className="aeline-mock__bar aeline-mock__bar--tall" />
                </div>
              </div>
              <h3>{t(`expertise.items.${key}.title`)}</h3>
              <p>{t(`expertise.items.${key}.desc`)}</p>
            </article>
          ))}
        </div>
      </section>

      <section id="pricing" className="aeline-section">
        <div className="aeline-container aeline-section__head--center">
          <div className="aeline-tag">
            <span className="aeline-tag__dot" />
            {t("pricing.tag")}
          </div>
          <h2 className="aeline-section__title">{t("pricing.title")}</h2>
          <p className="aeline-section__desc">{t("pricing.desc")}</p>
        </div>
        <div className="aeline-container aeline-pricing-grid">
          {(["starter", "growth", "enterprise"] as const).map((key) => (
            <article key={key} className={`aeline-pricing-card ${key === "growth" ? "is-featured" : ""}`}>
              <div className="aeline-pricing-card__head">
                <span className="aeline-pricing-card__plan">{t(`pricing.plans.${key}.name`)}</span>
                <p>{t(`pricing.plans.${key}.desc`)}</p>
              </div>
              <div className="aeline-pricing-card__price">{t(`pricing.plans.${key}.price`)}</div>
              <ul className="aeline-pricing-card__features">
                {(t.raw(`pricing.plans.${key}.features`) as string[]).map((f) => (
                  <li key={f}>{f}</li>
                ))}
              </ul>
              <AuthArrowButton href="#login" variant={key === "growth" ? "lime" : "dark"}>
                {t("pricing.cta")}
              </AuthArrowButton>
            </article>
          ))}
        </div>
      </section>

      <section className="aeline-section">
        <div className="aeline-container">
          <div className="aeline-section__head">
            <div className="aeline-tag">
              <span className="aeline-tag__dot" />
              {t("testimonials.tag")}
            </div>
            <h2 className="aeline-section__title">{t("testimonials.title")}</h2>
            <p className="aeline-section__desc">{t("testimonials.desc")}</p>
          </div>
          <div className="aeline-testimonials-scroll">
            {(["one", "two", "three"] as const).map((key, i) => (
              <article key={key} className="aeline-testimonial-card">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={TESTIMONIAL_IMAGES[i]} alt="" className="aeline-testimonial-card__img" loading="lazy" />
                <div className="aeline-testimonial-card__overlay">
                  <p>&ldquo;{t(`testimonials.items.${key}.text`)}&rdquo;</p>
                  <span>{t(`testimonials.items.${key}.author`)}</span>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="aeline-cta">
        <div className="aeline-container aeline-cta__inner">
          <p className="aeline-cta__eyebrow">{t("cta.eyebrow")}</p>
          <h2>{t("cta.title")}</h2>
          <p>{t("cta.desc")}</p>
          <AuthArrowButton href="#login">{t("cta.button")}</AuthArrowButton>
        </div>
      </section>

      <footer className="aeline-footer">
        <div className="aeline-container aeline-footer__grid">
          <div>
            <Link href="/" className="aeline-footer__brand">
              <TmbLogo className="w-8 h-8" />
              <span>TMB</span>
            </Link>
            <p className="aeline-footer__desc">{t("footer.desc")}</p>
          </div>
          <div className="aeline-footer__links">
            <div>
              <h4>{t("footer.platform")}</h4>
              <Link href="/">{t("footer.staff")}</Link>
              <Link href="/parent/login">{t("footer.parent")}</Link>
              <Link href="/verify">{t("footer.verify")}</Link>
            </div>
            <div>
              <h4>{t("footer.region")}</h4>
              <span>{t("footer.monitoring")}</span>
              <span>RBAC · MFA</span>
            </div>
          </div>
        </div>
        <div className="aeline-container aeline-footer__bottom">
          <span>{t("footer.copyright")}</span>
          <span>{t("footer.regionLabel")}</span>
        </div>
      </footer>
    </>
  );
}
