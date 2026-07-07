"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { DigitalClock } from "@/components/DigitalClock";
import { KpiCards } from "@/components/KpiCards";
import { OperatorDashboard } from "@/components/OperatorDashboard";
import { StatsChart } from "@/components/StatsChart";
import { getDashboardKpis, getMe } from "@/lib/api";

type DashData = {
  kpis: { key: string; value: number }[];
  daily_stats: { label: string; value: number }[];
  weekly_stats: { label: string; value: number }[];
  monthly_stats: { label: string; value: number }[];
};

function StaffDashboard() {
  const t = useTranslations("dashboard");
  const [dash, setDash] = useState<DashData | null>(null);
  const [userName, setUserName] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("tmb_access_token");
    if (!token) {
      window.location.href = "/";
      return;
    }
    Promise.all([getMe(), getDashboardKpis()])
      .then(([me, data]) => {
        if (me.success) setUserName(me.data.username || me.data.role);
        if (data.success) setDash(data.data as DashData);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-5">
      <div className="grid gap-4 lg:grid-cols-[1fr_minmax(280px,380px)]">
        <div className="rounded-lg border border-gray-200/80 dark:border-gray-800 bg-white dark:bg-gray-900 px-4 sm:px-5 py-4 shadow-sm flex flex-col justify-center">
          <h2 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-gray-100">{t("welcome")}</h2>
          {userName && (
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              <span className="inline-flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-emerald-500" aria-hidden />
                {userName}
              </span>
            </p>
          )}
        </div>
        <DigitalClock />
      </div>
      {loading ? (
        <p className="text-gray-400 dark:text-gray-500 text-sm px-1">{t("loading")}</p>
      ) : (
        <>
          <KpiCards kpis={dash?.kpis ?? []} />
          <div className="grid gap-3 lg:grid-cols-3">
            <StatsChart title={t("charts.daily")} data={dash?.daily_stats ?? []} />
            <StatsChart title={t("charts.weekly")} data={dash?.weekly_stats ?? []} />
            <StatsChart title={t("charts.monthly")} data={dash?.monthly_stats ?? []} />
          </div>
        </>
      )}
    </div>
  );
}

export default function DashboardPage() {
  const [role, setRole] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMe()
      .then((me) => {
        if (me.success) setRole(me.data.role);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return null;

  if (role === "hokimiyat_operator") {
    return <OperatorDashboard />;
  }

  return <StaffDashboard />;
}
