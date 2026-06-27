"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { CenterCertificatesChart } from "@/components/CenterCertificatesChart";
import { OperatorKpiCards } from "@/components/OperatorKpiCards";
import { TrendLineChart } from "@/components/TrendLineChart";
import { getMe, getOperatorSummary } from "@/lib/api";

type OperatorData = {
  active_centers: number;
  total_teachers: number;
  total_students: number;
  certificates_ytd: number;
  total_courses: number;
  certificates_by_center: {
    center_id: string;
    center_name: string;
    certificate_count: number;
  }[];
  certificates_by_center_total: number;
  student_trend: { label: string; value: number; is_forecast?: boolean }[];
  certificate_trend: { label: string; value: number; is_forecast?: boolean }[];
};

export function OperatorDashboard() {
  const t = useTranslations("operatorDashboard");
  const [data, setData] = useState<OperatorData | null>(null);
  const [userName, setUserName] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("tmb_access_token");
    if (!token) {
      window.location.href = "/";
      return;
    }
    Promise.all([getMe(), getOperatorSummary()])
      .then(([me, summary]) => {
        if (me.success) setUserName(me.data.username || me.data.role);
        if (summary.success) setData(summary.data as OperatorData);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">{t("welcome")}</h2>
        {userName && <p className="text-gray-500 mt-1">{userName}</p>}
        <p className="text-sm text-gray-400 mt-2 max-w-2xl">{t("subtitle")}</p>
      </div>

      {loading ? (
        <p className="text-gray-400">{t("loading")}</p>
      ) : data ? (
        <>
          <OperatorKpiCards data={data} />
          <div className="grid gap-6 lg:grid-cols-2">
            <CenterCertificatesChart
              title={t("charts.certificatesByCenter")}
              subtitle={t("charts.certificatesByCenterHint")}
              data={data.certificates_by_center}
              viewAllHref={
                data.certificates_by_center_total > 10 ? "/dashboard/certificates" : undefined
              }
              viewAllLabel={t("charts.viewAll")}
            />
            <TrendLineChart
              title={t("charts.studentTrend")}
              subtitle={t("charts.studentTrendHint")}
              data={data.student_trend}
              forecastLabel={t("charts.forecast")}
            />
          </div>
          <TrendLineChart
            title={t("charts.certificateTrend")}
            subtitle={t("charts.certificateTrendHint")}
            data={data.certificate_trend}
            forecastLabel={t("charts.forecast")}
          />
        </>
      ) : (
        <p className="text-red-500">{t("error")}</p>
      )}
    </div>
  );
}
