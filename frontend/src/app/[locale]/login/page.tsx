import {getTranslations} from 'next-intl/server';

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
        <section className="rounded-[2rem] border border-white/60 bg-white/80 p-10 shadow-card backdrop-blur dark:border-slate-800 dark:bg-slate-950/80">
          <p className="text-sm uppercase tracking-[0.35em] text-primary">{tCommon('governmentSubtitle')}</p>
          <h2 className="mt-5 max-w-2xl text-4xl font-semibold leading-tight text-ink dark:text-white">
            {tAuth('title')}
          </h2>
          <p className="mt-4 max-w-2xl text-base text-slate-600 dark:text-slate-300">{tAuth('subtitle')}</p>
          <div className="mt-10 grid gap-4 sm:grid-cols-2">
            <div className="rounded-2xl border border-primary/10 bg-primary/5 p-5">
              <h3 className="font-semibold text-primary">JWT + RS256</h3>
              <p className="mt-2 text-sm text-slate-600">15-minute access tokens and rotating secure refresh cookies.</p>
            </div>
            <div className="rounded-2xl border border-accent/20 bg-accent/10 p-5">
              <h3 className="font-semibold text-accent">TOTP MFA</h3>
              <p className="mt-2 text-sm text-slate-600">{tAuth('footer')}</p>
            </div>
          </div>
        </section>

        <section className="relative z-10 rounded-[2rem] border border-white/60 bg-white p-8 shadow-card dark:border-slate-800 dark:bg-slate-950">
          <form className="space-y-5">
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700 dark:text-slate-200">
                {tAuth('username')}
              </label>
              <input
                className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 outline-none ring-0 transition focus:border-primary dark:border-slate-800 dark:bg-slate-900"
                defaultValue="admin.tamor"
              />
            </div>
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700 dark:text-slate-200">
                {tAuth('password')}
              </label>
              <input
                type="password"
                className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 outline-none ring-0 transition focus:border-primary dark:border-slate-800 dark:bg-slate-900"
                defaultValue="Tamor#2026Admin!"
              />
            </div>
            <button
              type="button"
              className="w-full rounded-2xl bg-primary px-4 py-3 font-semibold text-white transition hover:bg-primary/90"
            >
              {tAuth('submit')}
            </button>
          </form>
          <p className="mt-5 text-sm text-slate-500 dark:text-slate-300">{tAuth('parentHint')}</p>
          <div className="mt-6 rounded-2xl border border-dashed border-slate-300 p-4 text-xs text-slate-500 dark:border-slate-700 dark:text-slate-400">
            <p className="font-semibold uppercase tracking-[0.2em]">Phase 0</p>
            <p className="mt-2">Locale route: /{locale}/login</p>
            <p className="mt-1">Backend base path: /api/v1/auth/*</p>
          </div>
          <Link
            href="/dashboard"
            className="mt-6 inline-flex text-sm font-semibold text-primary underline-offset-4 hover:underline"
          >
            {tCommon('dashboard')}
          </Link>
        </section>
      </div>
    </main>
  );
}
