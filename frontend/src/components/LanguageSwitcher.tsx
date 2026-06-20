"use client";

import { useRouter } from "next/navigation";
import { useLocale } from "next-intl";

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
    <div className="flex items-center gap-1 text-sm font-medium" role="group" aria-label="Language">
      {LOCALES.map(({ code, label }) => (
        <button
          key={code}
          type="button"
          onClick={() => switchLocale(code)}
          className={`px-2 py-1 rounded transition-colors ${
            locale === code
              ? "bg-naqsh-primary text-white"
              : "text-naqsh-primary hover:bg-naqsh-primary/10"
          }`}
        >
          {label}
        </button>
      ))}
    </div>
  );
}
