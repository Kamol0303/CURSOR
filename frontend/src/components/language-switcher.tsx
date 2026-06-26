'use client';

import {useLocale, useTranslations} from 'next-intl';

import {usePathname, useRouter} from '@/i18n/navigation';

const locales = ['uz', 'ru', 'en'] as const;

export function LanguageSwitcher() {
  const locale = useLocale();
  const t = useTranslations('common');
  const router = useRouter();
  const pathname = usePathname();

  return (
    <div className="flex items-center gap-1 rounded-full border border-white/40 bg-white/70 p-1 text-xs font-semibold uppercase tracking-[0.2em] text-[var(--foreground)] shadow-sm backdrop-blur dark:border-white/10 dark:bg-slate-900/50 dark:text-white">
      <span className="px-2 text-[10px] text-slate-500 dark:text-slate-300">{t('language')}</span>
      {locales.map((candidate) => {
        const active = locale === candidate;
        return (
          <button
            key={candidate}
            type="button"
            onClick={() => router.replace(pathname, {locale: candidate})}
            className={`rounded-full px-3 py-1 transition ${
              active ? 'bg-[var(--color-naqsh-primary)] text-white' : 'text-slate-600 hover:bg-slate-200 dark:text-slate-200 dark:hover:bg-slate-800'
            }`}
          >
            {candidate}
          </button>
        );
      })}
    </div>
  );
}
