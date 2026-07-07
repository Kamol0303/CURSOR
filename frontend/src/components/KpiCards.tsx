"use client";

import { useTranslations } from "next-intl";

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
  total_students: "border-l-[#1b4d3e]",
  active_students: "border-l-emerald-600",
  total_teachers: "border-l-[#c8932a]",
  total_centers: "border-l-[#1b4d3e]",
  total_courses: "border-l-sky-600",
  monthly_revenue: "border-l-[#c8932a]",
  debtors_count: "border-l-red-500",
  new_registrations_month: "border-l-violet-600",
};

const KPI_ICON: Record<(typeof KPI_KEYS)[number], string> = {
  total_students: "ST",
  active_students: "AC",
  total_teachers: "TH",
  total_centers: "BR",
  total_courses: "CR",
  monthly_revenue: "UZ",
  debtors_count: "DB",
  new_registrations_month: "NW",
};

export function KpiCards({ kpis }: { kpis: Kpi[] }) {
  const t = useTranslations("dashboard");
  const valueMap = Object.fromEntries(kpis.map((k) => [k.key, k.value]));

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-3">
      {KPI_KEYS.map((key) => {
        const raw = valueMap[key] ?? 0;
        const formatted =
          key === "monthly_revenue"
            ? `${new Intl.NumberFormat("uz-UZ").format(raw)} UZS`
            : new Intl.NumberFormat().format(raw);
        return (
          <div
            key={key}
            className={`group bg-white dark:bg-gray-900 rounded-lg border border-gray-200/80 dark:border-gray-800 border-l-4 ${KPI_ACCENT[key]} shadow-sm hover:shadow-md hover:border-naqsh-primary/20 dark:hover:border-naqsh-accent/30 transition-shadow duration-200 p-3.5 sm:p-4`}
          >
            <div className="flex items-start justify-between gap-2 mb-2">
              <p className="text-[11px] font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400 leading-snug">
                {t(`kpi.${key}`)}
              </p>
              <span
                className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-gray-50 dark:bg-gray-800 text-[10px] font-bold text-naqsh-primary dark:text-naqsh-accent"
                aria-hidden
              >
                {KPI_ICON[key]}
              </span>
            </div>
            <p className="text-xl sm:text-2xl font-bold text-naqsh-primary dark:text-naqsh-accent tabular-nums tracking-tight">
              {formatted}
            </p>
          </div>
        );
      })}
    </div>
  );
}
