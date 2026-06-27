"use client";

import { useTranslations } from "next-intl";

type OperatorSummary = {
  active_centers: number;
  total_teachers: number;
  total_students: number;
  certificates_ytd: number;
  total_courses: number;
};

const KPI_CONFIG = [
  { key: "active_centers", color: "from-emerald-500 to-emerald-600", icon: "🏫" },
  { key: "total_teachers", color: "from-sky-500 to-sky-600", icon: "👩‍🏫" },
  { key: "total_students", color: "from-violet-500 to-violet-600", icon: "🎓" },
  { key: "certificates_ytd", color: "from-amber-500 to-amber-600", icon: "📜" },
  { key: "total_courses", color: "from-rose-500 to-rose-600", icon: "📚" },
] as const;

export function OperatorKpiCards({ data }: { data: OperatorSummary }) {
  const t = useTranslations("operatorDashboard.kpi");
  const fmt = new Intl.NumberFormat("uz-UZ");

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-5 gap-4">
      {KPI_CONFIG.map(({ key, color, icon }) => (
        <div
          key={key}
          className={`rounded-2xl bg-gradient-to-br ${color} text-white p-5 shadow-md hover:shadow-lg transition-shadow`}
        >
          <div className="flex items-start justify-between gap-2">
            <span className="text-2xl opacity-90" aria-hidden>
              {icon}
            </span>
          </div>
          <p className="mt-3 text-3xl font-bold tracking-tight">{fmt.format(data[key])}</p>
          <p className="mt-1 text-sm text-white/85">{t(key)}</p>
        </div>
      ))}
    </div>
  );
}
