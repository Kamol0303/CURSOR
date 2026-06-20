import type {ReactNode} from 'react';

import {NextIntlClientProvider, hasLocale} from 'next-intl';
import {getMessages, setRequestLocale} from 'next-intl/server';
import {notFound} from 'next/navigation';

import {LanguageSwitcher} from '@/components/language-switcher';
import {routing} from '@/i18n/routing';

import '../globals.css';

type Props = {
  children: ReactNode;
  params: Promise<{locale: string}>;
};

export default async function LocaleLayout({children, params}: Props) {
  const {locale} = await params;

  if (!hasLocale(routing.locales, locale)) {
    notFound();
  }

  setRequestLocale(locale);
  const messages = await getMessages();

  return (
    <html lang={locale}>
      <body className="min-h-screen bg-[var(--background)] text-[var(--foreground)]">
        <NextIntlClientProvider messages={messages}>
          <div className="relative min-h-screen">
            <header className="mx-auto flex max-w-7xl items-center justify-between px-6 py-6">
              <div>
                <p className="text-xs uppercase tracking-[0.35em] text-primary">TaMoR</p>
                <h1 className="text-lg font-semibold">District Education Monitoring &amp; Rating</h1>
              </div>
              <LanguageSwitcher />
            </header>
            {children}
          </div>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
