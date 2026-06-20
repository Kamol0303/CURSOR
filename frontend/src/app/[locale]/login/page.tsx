import {getTranslations} from 'next-intl/server';

import {LoginForm} from '@/components/auth/login-form';
import {GirihBackground} from '@/components/girih-background';
import {Link} from '@/i18n/navigation';

type Props = {
  params: Promise<{locale: string}>;
};

export default async function LoginPage({params}: Props) {
  const {locale} = await params;
  const tAuth = await getTranslations('auth');
  const tCommon = await getTranslations('common');

  return (
    <main className="relative mx-auto flex min-h-[calc(100vh-96px)] w-full max-w-7xl items-center justify-center overflow-hidden px-6 pb-10">
      <GirihBackground opacity={0.05} />
      <div className="relative z-10 grid w-full max-w-6xl gap-8 lg:grid-cols-[1.2fr_0.9fr]">
        <section className="rounded-[2rem] border border-white/60 bg-white/80 p-10 shadow-[0_18px_48px_rgba(15,30,24,0.12)] backdrop-blur dark:border-slate-800 dark:bg-slate-950/80">
          <p className="text-sm uppercase tracking-[0.35em] text-[var(--color-naqsh-primary)]">{tCommon('governmentSubtitle')}</p>
          <h2 className="mt-5 max-w-2xl text-4xl font-semibold leading-tight text-[var(--foreground)] dark:text-white">
            {tAuth('title')}
          </h2>
          <p className="mt-4 max-w-2xl text-base text-slate-600 dark:text-slate-300">{tAuth('subtitle')}</p>
          <div className="mt-10 grid gap-4 sm:grid-cols-2">
            <div className="rounded-2xl border border-[rgba(27,77,62,0.12)] bg-[rgba(27,77,62,0.05)] p-5">
              <h3 className="font-semibold text-[var(--color-naqsh-primary)]">JWT + RS256</h3>
              <p className="mt-2 text-sm text-slate-600">15-minute access tokens and rotating secure refresh cookies.</p>
            </div>
            <div className="rounded-2xl border border-[rgba(200,147,42,0.2)] bg-[rgba(200,147,42,0.12)] p-5">
              <h3 className="font-semibold text-[var(--color-naqsh-accent)]">TOTP MFA</h3>
              <p className="mt-2 text-sm text-slate-600">{tAuth('footer')}</p>
            </div>
          </div>
        </section>

        <section className="relative z-10 rounded-[2rem] border border-white/60 bg-white p-8 shadow-[0_18px_48px_rgba(15,30,24,0.12)] dark:border-slate-800 dark:bg-slate-950">
          <LoginForm locale={locale} />
          <p className="mt-5 text-sm text-slate-500 dark:text-slate-300">{tAuth('parentHint')}</p>
          <div className="mt-6 rounded-2xl border border-dashed border-slate-300 p-4 text-xs text-slate-500 dark:border-slate-700 dark:text-slate-400">
            <p className="font-semibold uppercase tracking-[0.2em]">Phase 0</p>
            <p className="mt-2">Locale route: /{locale}/login</p>
            <p className="mt-1">Backend base path: /api/v1/auth/*</p>
          </div>
          <Link
            href="/dashboard"
            className="mt-6 inline-flex text-sm font-semibold text-[var(--color-naqsh-primary)] underline-offset-4 hover:underline"
          >
            {tCommon('dashboard')}
          </Link>
        </section>
      </div>
    </main>
  );
}
