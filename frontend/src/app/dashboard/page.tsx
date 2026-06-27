"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
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
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">{t("welcome")}</h2>
        {userName && <p className="text-gray-500 mt-1">{userName}</p>}
      </div>
      {loading ? (
        <p className="text-gray-400">{t("loading")}</p>
      ) : (
        <>
          <KpiCards kpis={dash?.kpis ?? []} />
          <div className="grid gap-4 lg:grid-cols-3">
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
