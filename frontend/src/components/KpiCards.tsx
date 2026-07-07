"use client";

import { useTranslations } from "next-intl";
import { BezelCard } from "@/components/ui";

type Kpi = { key: string; value: number };

const KPI_KEYS = [
  "total_students",
  "active_students",
  "total_teachers",
  "total_centers",
  "total_courses",
  "monthly_revenue",
  "debtors_count",
  "new_registrations_month",
] as const;

const KPI_ACCENT: Record<(typeof KPI_KEYS)[number], string> = {
  total_students: "from-naqsh-primary/90 to-naqsh-primary/50",
  active_students: "from-emerald-600/90 to-emerald-600/50",
  total_teachers: "from-naqsh-accent/90 to-naqsh-accent/50",
  total_centers: "from-naqsh-primary/90 to-naqsh-primary/50",
  total_courses: "from-sky-600/90 to-sky-600/50",
  monthly_revenue: "from-naqsh-accent/90 to-naqsh-accent/50",
  debtors_count: "from-red-500/90 to-red-500/50",
  new_registrations_month: "from-violet-600/90 to-violet-600/50",
};

export function KpiCards({ kpis }: { kpis: Kpi[] }) {
  const t = useTranslations("dashboard");
  const valueMap = Object.fromEntries(kpis.map((k) => [k.key, k.value]));

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-4">
      {KPI_KEYS.map((key, i) => {
        const raw = valueMap[key] ?? 0;
        const formatted =
          key === "monthly_revenue"
            ? `${new Intl.NumberFormat("uz-UZ").format(raw)} UZS`
            : new Intl.NumberFormat().format(raw);
        return (
          <BezelCard
            key={key}
            hover
            className="animate-slide-up"
            padding="p-1"
          >
            <div
              className="relative overflow-hidden p-4 sm:p-5"
              style={{ animationDelay: `${i * 40}ms` }}
            >
              <div
                className={`absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r ${KPI_ACCENT[key]}`}
                aria-hidden
              />
              <p className="text-caption font-medium uppercase tracking-wider text-muted-foreground leading-snug mb-2">
                {t(`kpi.${key}`)}
              </p>
              <p className="text-h2 text-naqsh-primary dark:text-naqsh-accent tabular-nums tracking-tight">
                {formatted}
              </p>
            </div>
          </BezelCard>
        );
      })}
    </div>
  );
}
