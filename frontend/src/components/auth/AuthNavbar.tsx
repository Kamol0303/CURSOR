"use client";

import Link from "next/link";
import { useState } from "react";
import { usePathname } from "next/navigation";
import { useTranslations } from "next-intl";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { ThemeToggle } from "@/components/ThemeToggle";
import { TmbLogo } from "@/components/TmbLogo";
import { AuthArrowButton, AuthButton } from "@/components/AuthButton";

export function AuthNavbar() {
  const t = useTranslations("auth");
  const tLand = useTranslations("auth.landing");
  const pathname = usePathname();
  const isParent = pathname?.startsWith("/parent");
  const [open, setOpen] = useState(false);

  const navLinks = [
    { href: "#about", label: tLand("nav.about") },
    { href: "#services", label: tLand("nav.services") },
    { href: "#pricing", label: tLand("nav.pricing") },
    { href: "/verify", label: t("footer.verify") },
  ];

  return (
    <header className="aeline-navbar">
      <div className="aeline-container aeline-navbar__inner">
        <Link href="/" className="aeline-navbar__logo">
          <TmbLogo className="w-9 h-9" />
          <span>TMB</span>
        </Link>

        <nav className={`aeline-navbar__nav ${open ? "is-open" : ""}`} aria-label="Main">
          <Link href="/" className={!isParent ? "is-active" : ""} onClick={() => setOpen(false)}>
            {t("footer.staff")}
          </Link>
          <Link href="/parent/login" className={isParent ? "is-active" : ""} onClick={() => setOpen(false)}>
            {t("footer.parent")}
          </Link>
          {navLinks.map((l) => (
            <Link key={l.href} href={l.href} onClick={() => setOpen(false)}>
              {l.label}
            </Link>
          ))}
        </nav>

        <div className="aeline-navbar__actions">
          <ThemeToggle />
          <LanguageSwitcher />
          <span className="hidden md:inline-flex">
            <AuthButton
              variant="dark"
              fullWidth={false}
              type="button"
              onClick={() => {
                document.getElementById("login")?.scrollIntoView({ behavior: "smooth" });
              }}
            >
              {tLand("nav.login")}
            </AuthButton>
          </span>
          <button
            type="button"
            className="aeline-navbar__menu"
            aria-label="Menu"
            aria-expanded={open}
            onClick={() => setOpen((v) => !v)}
          >
            <span />
            <span />
            <span />
          </button>
        </div>
      </div>
    </header>
  );
}

export function AuthHeroRating() {
  const t = useTranslations("auth.landing");
  return (
    <div className="aeline-hero__rating">
      <p>{t("hero.rating")}</p>
      <div className="aeline-hero__stars" aria-hidden>
        {Array.from({ length: 5 }).map((_, i) => (
          <svg key={i} viewBox="0 0 16 16" className="aeline-hero__star">
            <path d="M3.88 14L4.97 9.32 1.33 6.17 6.13 5.75 8 1.33 9.87 5.75 14.67 6.17 11.03 9.32 12.12 14 8 11.52 3.88 14Z" fill="currentColor" />
          </svg>
        ))}
      </div>
    </div>
  );
}

export function AuthHeroActions() {
  const t = useTranslations("auth.landing");
  return (
    <div className="aeline-hero__actions">
      <AuthButton
        variant="secondary"
        fullWidth={false}
        type="button"
        onClick={() => document.getElementById("about")?.scrollIntoView({ behavior: "smooth" })}
      >
        {t("hero.demo")}
      </AuthButton>
      <AuthArrowButton href="#login">{t("hero.cta")}</AuthArrowButton>
    </div>
  );
}
