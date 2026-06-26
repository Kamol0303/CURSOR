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

export function KpiCards({ kpis }: { kpis: Kpi[] }) {
  const t = useTranslations("dashboard");
  const valueMap = Object.fromEntries(kpis.map((k) => [k.key, k.value]));

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {KPI_KEYS.map((key) => {
        const raw = valueMap[key] ?? 0;
        const formatted =
          key === "monthly_revenue"
            ? new Intl.NumberFormat("uz-UZ").format(raw) + " UZS"
            : new Intl.NumberFormat().format(raw);
        return (
          <div
            key={key}
            className="bg-white rounded-xl border border-gray-100 shadow-sm p-5 hover:shadow-md transition-shadow"
          >
            <p className="text-sm text-gray-500 mb-1">{t(`kpi.${key}`)}</p>
            <p className="text-2xl font-bold text-naqsh-primary">{formatted}</p>
          </div>
        );
      })}
    </div>
  );
}
