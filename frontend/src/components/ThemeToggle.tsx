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

  if (!mounted) {
    return (
      <button
        type="button"
        className="p-2 rounded-lg border border-naqsh-primary/20 text-naqsh-primary opacity-60"
        aria-label={t("themeToggle")}
        disabled
      >
        ◐
      </button>
    );
  }

  const isDark = theme === "dark";

  return (
    <button
      type="button"
      onClick={toggleTheme}
      className="p-2 rounded-lg border border-naqsh-primary/20 text-naqsh-primary hover:bg-naqsh-primary/10 dark:border-white/20 dark:text-naqsh-accent dark:hover:bg-white/10 transition-colors"
      aria-label={isDark ? t("themeLight") : t("themeDark")}
      title={isDark ? t("themeLight") : t("themeDark")}
    >
      {isDark ? "☀️" : "🌙"}
    </button>
  );
}
