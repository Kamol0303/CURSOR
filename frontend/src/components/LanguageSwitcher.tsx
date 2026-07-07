"use client";

import { useRouter } from "next/navigation";
import { useLocale } from "next-intl";
import { cn } from "@/lib/cn";

const LOCALES = [
  { code: "uz", label: "UZ" },
  { code: "ru", label: "RU" },
  { code: "en", label: "EN" },
] as const;

export function LanguageSwitcher() {
  const locale = useLocale();
  const router = useRouter();

  const switchLocale = (code: string) => {
    document.cookie = `NEXT_LOCALE=${code};path=/;max-age=31536000;SameSite=Strict`;
    router.refresh();
  };

  return (
    <div
      className="flex items-center gap-0.5 p-0.5 rounded-lg bg-muted border border-border"
      role="group"
      aria-label="Language"
    >
      {LOCALES.map(({ code, label }) => (
        <button
          key={code}
          type="button"
          onClick={() => switchLocale(code)}
          className={cn(
            "px-2.5 py-1 rounded-md text-caption font-medium transition-all duration-fast",
            locale === code
              ? "bg-surface dark:bg-card text-naqsh-primary dark:text-naqsh-accent shadow-sm"
              : "text-muted-foreground hover:text-foreground",
          )}
          aria-pressed={locale === code}
        >
          {label}
        </button>
      ))}
    </div>
  );
}
