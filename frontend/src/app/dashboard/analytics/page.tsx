"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { DashboardLayout } from "@/components/DashboardLayout";
import { apiFetch } from "@/lib/api";

type Prediction = {
  prediction_type: string;
  payload: Record<string, unknown>;
  confidence_score: number;
  period_start?: string;
  period_end?: string;
};

export default function AnalyticsPage() {
  const t = useTranslations("analytics");
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastRun, setLastRun] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    apiFetch<{ predictions: Prediction[]; last_run: Record<string, unknown> | null }>("/analytics/insights")
      .then((res) => {
        if (res.success && res.data) {
          setPredictions(res.data.predictions || []);
          setLastRun(res.data.last_run || null);
        }
      })
      .finally(() => setLoading(false));
  }, []);

  const typeLabel = (type: string) => {
    const key = type as "fastest_growing_center" | "declining_centers" | "high_demand_subjects" | "education_gap_index";
    return t(`types.${key}`, { defaultValue: type });
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-naqsh-primary">{t("title")}</h2>
          <p className="text-gray-600 text-sm mt-1">{t("subtitle")}</p>
        </div>

        {loading ? (
          <p className="text-gray-500">{t("loading")}</p>
        ) : predictions.length === 0 ? (
          <p className="text-gray-500">{t("empty")}</p>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {predictions.map((p) => (
              <div key={p.prediction_type} className="bg-white rounded-xl border p-5 shadow-sm">
                <div className="flex justify-between items-start mb-3">
                  <h3 className="font-semibold text-naqsh-primary">{typeLabel(p.prediction_type)}</h3>
                  <span className="text-xs bg-emerald-50 text-emerald-700 px-2 py-1 rounded-full">
                    {Math.round(p.confidence_score * 100)}%
                  </span>
                </div>
                <PredictionBody type={p.prediction_type} payload={p.payload} t={t} />
              </div>
            ))}
          </div>
        )}

        {lastRun && (
          <p className="text-xs text-gray-400">
            {t("lastRun")}: {String(lastRun.created_at ?? "—")}
          </p>
        )}
      </div>
    </DashboardLayout>
  );
}

function PredictionBody({
  type,
  payload,
  t,
}: {
  type: string;
  payload: Record<string, unknown>;
  t: ReturnType<typeof useTranslations>;
}) {
  if (type === "fastest_growing_center" && payload.center_name) {
    return (
      <div className="text-sm text-gray-700 space-y-1">
        <p>
          <strong>{String(payload.center_name)}</strong>
        </p>
        <p>
          {t("newStudents")}: {String(payload.new_students ?? 0)} ({String(payload.growth_rate_pct ?? 0)}%)
        </p>
      </div>
    );
  }

  if (type === "declining_centers") {
    const centers = (payload.centers as Array<Record<string, unknown>>) || [];
    if (!centers.length) return <p className="text-sm text-gray-500">{t("noDeclining")}</p>;
    return (
      <ul className="text-sm text-gray-700 space-y-1">
        {centers.map((c) => (
          <li key={String(c.center_id)}>
            {String(c.center_name)} — {t("rankDrop")}: {String(c.rank_drop)}
          </li>
        ))}
      </ul>
    );
  }

  if (type === "high_demand_subjects") {
    const subjects = (payload.subjects as Array<Record<string, unknown>>) || [];
    return (
      <ul className="text-sm text-gray-700 space-y-1">
        {subjects.map((s) => (
          <li key={String(s.subject_id)}>
            {String(s.name_uz)} ({String(s.teacher_count)} {t("teachers")})
          </li>
        ))}
      </ul>
    );
  }

  if (type === "education_gap_index") {
    return (
      <div className="text-sm text-gray-700 space-y-1">
        <p className="text-3xl font-bold text-naqsh-accent">{String(payload.gap_index ?? "—")}</p>
        <p>
          {t("certRate")}: {String(payload.certification_rate_pct ?? 0)}%
        </p>
        <p>
          {t("studentTeacherRatio")}: {String(payload.student_teacher_ratio ?? "—")}
        </p>
      </div>
    );
  }

  return <pre className="text-xs text-gray-500 overflow-auto">{JSON.stringify(payload, null, 2)}</pre>;
}
