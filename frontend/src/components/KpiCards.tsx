"use client";

import { useTranslations } from "next-intl";

type Kpi = { key: string; value: number };

const KPI_KEYS = [
  "total_centers",
  "total_students",
  "total_teachers",
  "total_subjects",
  "active_centers",
  "new_registrations_month",
  "license_expiring_30_days",
] as const;

export function KpiCards({ kpis }: { kpis: Kpi[] }) {
  const t = useTranslations("dashboard");

  const valueMap = Object.fromEntries(kpis.map((k) => [k.key, k.value]));

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {KPI_KEYS.map((key) => (
        <div
          key={key}
          className="bg-white rounded-xl border border-gray-100 shadow-sm p-5 hover:shadow-md transition-shadow"
        >
          <p className="text-sm text-gray-500 mb-1">{t(`kpi.${key}`)}</p>
          <p className="text-3xl font-bold text-naqsh-primary">
            {new Intl.NumberFormat().format(valueMap[key] ?? 0)}
          </p>
        </div>
      ))}
    </div>
  );
}
