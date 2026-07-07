"use client";

import { useTranslations } from "next-intl";
import { BezelCard } from "@/components/ui";

type OperatorSummary = {
  active_centers: number;
  total_teachers: number;
  total_students: number;
  certificates_ytd: number;
  total_courses: number;
};

const KPI_CONFIG = [
  { key: "active_centers", accent: "from-emerald-600/90 to-emerald-600/50" },
  { key: "total_teachers", accent: "from-sky-600/90 to-sky-600/50" },
  { key: "total_students", accent: "from-violet-600/90 to-violet-600/50" },
  { key: "certificates_ytd", accent: "from-naqsh-accent/90 to-naqsh-accent/50" },
  { key: "total_courses", accent: "from-rose-600/90 to-rose-600/50" },
] as const;

export function OperatorKpiCards({ data }: { data: OperatorSummary }) {
  const t = useTranslations("operatorDashboard.kpi");
  const fmt = new Intl.NumberFormat("uz-UZ");

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-5 gap-4">
      {KPI_CONFIG.map(({ key, accent }, i) => (
        <div key={key} className="animate-slide-up" style={{ animationDelay: `${i * 50}ms` }}>
          <BezelCard hover padding="p-1">
          <div className="relative p-5 overflow-hidden">
            <div className={`absolute inset-x-0 top-0 h-0.5 bg-gradient-to-r ${accent}`} aria-hidden />
            <p className="text-h2 text-naqsh-primary dark:text-naqsh-accent tabular-nums tracking-tight">
              {fmt.format(data[key])}
            </p>
            <p className="mt-1 text-small text-muted-foreground">{t(key)}</p>
          </div>
        </BezelCard>
        </div>
      ))}
    </div>
  );
}
