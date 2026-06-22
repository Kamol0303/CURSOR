"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { KpiCards } from "@/components/KpiCards";
import { getDashboardKpis, getMe } from "@/lib/api";

export default function DashboardPage() {
  const t = useTranslations("dashboard");
  const [kpis, setKpis] = useState<{ key: string; value: number }[]>([]);
  const [userName, setUserName] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("tmb_access_token");
    if (!token) {
      window.location.href = "/";
      return;
    }
    Promise.all([getMe(), getDashboardKpis()])
      .then(([me, dash]) => {
        if (me.success) setUserName(me.data.username || me.data.role);
        if (dash.success) setKpis(dash.data.kpis);
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
          <KpiCards kpis={kpis} />
        )}
      </div>
    
  );
}
