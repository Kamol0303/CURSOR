'use client';

import { useLocale } from 'next-intl';
import { useRouter } from 'next/navigation';
import { useTransition } from 'react';
import { locales, type Locale } from '@/i18n/config';

const LOCALE_LABELS: Record<Locale, string> = {
  uz: 'UZ',
  ru: 'RU',
  en: 'EN',
};

export function LanguageSwitcher() {
  const locale = useLocale() as Locale;
  const router = useRouter();
  const [isPending, startTransition] = useTransition();

  const switchLocale = (newLocale: Locale) => {
    document.cookie = `NEXT_LOCALE=${newLocale};path=/;max-age=31536000;SameSite=Strict`;
    startTransition(() => {
      router.refresh();
    });
  };

  return (
    <div className="flex items-center gap-1 text-sm font-medium" role="group" aria-label="Language switcher">
      {locales.map((loc, i) => (
        <span key={loc} className="flex items-center">
          {i > 0 && <span className="mx-1 text-[var(--muted-foreground)]">|</span>}
          <button
            onClick={() => switchLocale(loc)}
            disabled={isPending}
            className={`px-1.5 py-0.5 rounded transition-colors ${
              locale === loc
                ? 'text-[var(--primary)] font-bold'
                : 'text-[var(--muted-foreground)] hover:text-[var(--foreground)]'
            }`}
            aria-current={locale === loc ? 'true' : undefined}
          >
            {LOCALE_LABELS[loc]}
          </button>
        </span>
      ))}
    </div>
  );
}
