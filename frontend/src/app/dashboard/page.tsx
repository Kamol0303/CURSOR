'use client';

import { useTranslations, useLocale } from 'next-intl';
import { TamorLogo } from '@/components/ui/GirihPattern';
import { LanguageSwitcher } from '@/components/ui/LanguageSwitcher';
import { apiLogout } from '@/lib/api';
import { useRouter } from 'next/navigation';

const DEMO_KPIS = [
  { key: 'centers' as const, value: 47, change: 3.2 },
  { key: 'students' as const, value: 12840, change: 5.8 },
  { key: 'teachers' as const, value: 386, change: 1.4 },
  { key: 'certificates' as const, value: 2156, change: 12.1 },
];

export default function DashboardPage() {
  const t = useTranslations('dashboard');
  const tn = useTranslations('nav');
  const tc = useTranslations('common');
  const locale = useLocale();
  const router = useRouter();

  const formatNumber = (n: number) => new Intl.NumberFormat(locale).format(n);

  const handleLogout = async () => {
    await apiLogout();
    router.push('/login');
  };

  return (
    <div className="min-h-screen bg-[var(--background)]">
      <header className="border-b border-[var(--border)] bg-[var(--card)]">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <TamorLogo size={32} />
          <nav className="hidden md:flex items-center gap-6 text-sm">
            <span className="font-medium text-[var(--primary)]">{tn('dashboard')}</span>
            <span className="text-[var(--muted-foreground)]">{tn('centers')}</span>
            <span className="text-[var(--muted-foreground)]">{tn('students')}</span>
            <span className="text-[var(--muted-foreground)]">{tn('ratings')}</span>
          </nav>
          <div className="flex items-center gap-4">
            <LanguageSwitcher />
            <button onClick={handleLogout} className="text-sm text-[var(--muted-foreground)] hover:text-[var(--foreground)]">
              {tc('logout')}
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-6">{t('title')}</h1>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {DEMO_KPIS.map((kpi) => (
            <div key={kpi.key} className="card p-5">
              <p className="text-sm text-[var(--muted-foreground)] mb-1">
                {t(`kpi.${kpi.key}`, { count: kpi.value })}
              </p>
              <p className="text-3xl font-bold">{formatNumber(kpi.value)}</p>
              <p className={`text-sm mt-1 ${kpi.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {kpi.change >= 0 ? '↑' : '↓'} {Math.abs(kpi.change)}%
              </p>
            </div>
          ))}
        </div>

        <div className="mt-8 card p-6">
          <p className="text-[var(--muted-foreground)]">
            Phase 0 foundation complete. Full dashboard charts and data integration in Phase 1.
          </p>
        </div>
      </main>
    </div>
  );
}
