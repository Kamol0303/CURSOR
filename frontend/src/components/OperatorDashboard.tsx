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

type TrendVariant = "students" | "certificates" | null;

export function OperatorDashboard({ trendVariant }: { trendVariant: TrendVariant }) {
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

  const trendData =
    trendVariant === "certificates"
      ? data?.certificate_trend ?? []
      : trendVariant === "students"
        ? data?.student_trend ?? []
        : [];

  const trendTitle =
    trendVariant === "certificates" ? t("charts.certificateTrend") : t("charts.studentTrend");
  const trendSubtitle =
    trendVariant === "certificates"
      ? t("charts.certificateTrendHint")
      : t("charts.studentTrendHint");

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
            {trendVariant ? (
              <TrendLineChart
                title={trendTitle}
                subtitle={trendSubtitle}
                data={trendData}
                forecastLabel={t("charts.forecast")}
              />
            ) : (
              <div className="bg-white rounded-2xl border border-dashed border-gray-200 p-8 flex items-center justify-center text-center text-gray-500 text-sm">
                {t("charts.trendPlaceholder")}
              </div>
            )}
          </div>
        </>
      ) : (
        <p className="text-red-500">{t("error")}</p>
      )}
    </div>
  );
}
