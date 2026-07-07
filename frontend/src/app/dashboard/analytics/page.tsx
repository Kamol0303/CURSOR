"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import {
  Badge,
  Card,
  CardBody,
  CardTitle,
  EmptyState,
  PageHeader,
  PageSection,
  CardSkeleton,
} from "@/components/ui";
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
    <PageSection>
      <PageHeader title={t("title")} description={t("subtitle")} />

      {loading ? (
        <div className="grid gap-4 md:grid-cols-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
      ) : predictions.length === 0 ? (
        <EmptyState title={t("empty")} />
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {predictions.map((p) => (
            <Card key={p.prediction_type} hover>
              <CardBody>
                <div className="flex justify-between items-start mb-3">
                  <CardTitle>{typeLabel(p.prediction_type)}</CardTitle>
                  <Badge variant="success">{Math.round(p.confidence_score * 100)}%</Badge>
                </div>
                <PredictionBody type={p.prediction_type} payload={p.payload} t={t} />
              </CardBody>
            </Card>
          ))}
        </div>
      )}

      {lastRun && (
        <p className="text-caption text-muted-foreground">
          {t("lastRun")}: {String(lastRun.created_at ?? "—")}
        </p>
      )}
    </PageSection>
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
      <div className="text-small text-muted-foreground space-y-1">
        <p>
          <strong className="text-foreground">{String(payload.center_name)}</strong>
        </p>
        <p>
          {t("newStudents")}: {String(payload.new_students ?? 0)} ({String(payload.growth_rate_pct ?? 0)}%)
        </p>
      </div>
    );
  }

  if (type === "declining_centers") {
    const centers = (payload.centers as Array<Record<string, unknown>>) || [];
    if (!centers.length) return <p className="text-small text-muted-foreground">{t("noDeclining")}</p>;
    return (
      <ul className="text-small text-muted-foreground space-y-1">
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
      <ul className="text-small text-muted-foreground space-y-1">
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
      <div className="text-small text-muted-foreground space-y-1">
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

  return <pre className="text-caption text-muted-foreground overflow-auto">{JSON.stringify(payload, null, 2)}</pre>;
}
