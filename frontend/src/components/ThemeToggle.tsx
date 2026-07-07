"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { applyTheme, resolveTheme, type Theme, THEME_STORAGE_KEY } from "@/lib/theme";

export function ThemeToggle() {
  const t = useTranslations("common");
  const [theme, setTheme] = useState<Theme>("light");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const initial = resolveTheme();
    setTheme(initial);
    applyTheme(initial);
    setMounted(true);
  }, []);

  const toggleTheme = () => {
    const next: Theme = theme === "dark" ? "light" : "dark";
    setTheme(next);
    localStorage.setItem(THEME_STORAGE_KEY, next);
    applyTheme(next);
  };

  const isDark = theme === "dark";
  const isLit = isDark;

  if (!mounted) {
    return (
      <button
        type="button"
        className="candle-toggle opacity-60"
        aria-label={t("themeToggle")}
        disabled
      >
        <span className="candle-toggle__scene" aria-hidden>
          <span className="candle-toggle__wave" />
          <span className="candle-toggle__candle">
            <span className="candle-toggle__wick" />
            <span className="candle-toggle__body">
              <span className="candle-toggle__eyes">
                <span className="candle-toggle__eye candle-toggle__eye--left" />
                <span className="candle-toggle__eye candle-toggle__eye--right" />
              </span>
            </span>
            <span className="candle-toggle__flame" />
          </span>
          <span className="candle-toggle__floor" />
        </span>
      </button>
    );
  }

  return (
    <button
      type="button"
      onClick={toggleTheme}
      className={`candle-toggle ${isLit ? "candle-toggle--lit" : ""}`}
      aria-label={isDark ? t("themeLight") : t("themeDark")}
      title={isDark ? t("themeLight") : t("themeDark")}
      aria-pressed={isDark}
    >
      <span className="candle-toggle__scene" aria-hidden>
        <span className="candle-toggle__wave" />
        <span className="candle-toggle__candle">
          <span className="candle-toggle__wick" />
          <span className="candle-toggle__body">
            <span className="candle-toggle__eyes">
              <span className="candle-toggle__eye candle-toggle__eye--left" />
              <span className="candle-toggle__eye candle-toggle__eye--right" />
            </span>
          </span>
          <span className="candle-toggle__flame" />
        </span>
        <span className="candle-toggle__floor" />
      </span>
    </button>
  );
}
