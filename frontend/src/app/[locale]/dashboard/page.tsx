import {getFormatter, getTranslations} from 'next-intl/server';

import {MetricCard} from '@/components/metric-card';

export default async function DashboardPage() {
  const t = await getTranslations('dashboard');
  const format = await getFormatter();
  const now = new Date('2026-06-20T11:00:00Z');

  return (
    <main className="mx-auto max-w-7xl px-6 pb-16">
      <section className="rounded-[2rem] border border-slate-200 bg-white/90 p-8 shadow-[0_18px_48px_rgba(15,30,24,0.12)] backdrop-blur dark:border-slate-800 dark:bg-slate-950/80">
        <p className="text-sm uppercase tracking-[0.35em] text-[var(--color-naqsh-primary)]">{t('welcome')}</p>
        <h2 className="mt-3 text-3xl font-semibold text-[var(--foreground)] dark:text-white">{t('kpiTitle')}</h2>
        <p className="mt-3 text-sm text-slate-500 dark:text-slate-400">
          {t('lastUpdated', {date: now})}
        </p>
        <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <MetricCard label={t('centers', {count: 512})} value={format.number(512)} delta="+4.2%" />
          <MetricCard label={t('students', {count: 50234})} value={format.number(50234)} delta="+8.1%" />
          <MetricCard label={t('teachers', {count: 2014})} value={format.number(2014)} delta="+2.3%" />
          <MetricCard label={t('certificates', {count: 11876})} value={format.number(11876)} delta="+5.9%" />
        </div>
      </section>
    </main>
  );
}
