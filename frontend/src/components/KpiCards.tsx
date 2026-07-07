"use client";

import { useTranslations } from "next-intl";
import { Card } from "@/components/ui";

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
  total_students: "from-naqsh-primary/80 to-naqsh-primary/40",
  active_students: "from-emerald-600/80 to-emerald-600/40",
  total_teachers: "from-naqsh-accent/80 to-naqsh-accent/40",
  total_centers: "from-naqsh-primary/80 to-naqsh-primary/40",
  total_courses: "from-sky-600/80 to-sky-600/40",
  monthly_revenue: "from-naqsh-accent/80 to-naqsh-accent/40",
  debtors_count: "from-red-500/80 to-red-500/40",
  new_registrations_month: "from-violet-600/80 to-violet-600/40",
};

export function KpiCards({ kpis }: { kpis: Kpi[] }) {
  const t = useTranslations("dashboard");
  const valueMap = Object.fromEntries(kpis.map((k) => [k.key, k.value]));

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-4">
      {KPI_KEYS.map((key) => {
        const raw = valueMap[key] ?? 0;
        const formatted =
          key === "monthly_revenue"
            ? `${new Intl.NumberFormat("uz-UZ").format(raw)} UZS`
            : new Intl.NumberFormat().format(raw);
        return (
          <Card
            key={key}
            hover
            className="relative overflow-hidden p-4 sm:p-5 group transition-all duration-fast"
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
          </Card>
        );
      })}
    </div>
  );
}
