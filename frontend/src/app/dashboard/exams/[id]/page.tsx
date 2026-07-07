"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { PermissionGate } from "@/components/PermissionGate";
import {
  Badge,
  Button,
  Card,
  CardBody,
  CardTitle,
  EmptyState,
  PageHeader,
  PageSection,
  PageSkeleton,
} from "@/components/ui";
import { apiFetch } from "@/lib/api";
import { usePermissions } from "@/hooks/usePermissions";

type Question = {
  id: string;
  question_text: string;
  options_json: string[] | null;
  correct_answer: string | null;
  points: number;
};

type ExamDetail = {
  id: string;
  title: string;
  description: string | null;
  pass_score: number;
  duration_minutes: number;
  is_published: boolean;
  questions: Question[];
};

type Result = {
  id: string;
  student_id: string;
  score: number;
  max_score: number;
  passed: boolean;
};

export default function ExamDetailPage() {
  const t = useTranslations("exams");
  const params = useParams();
  const examId = params.id as string;
  const { can } = usePermissions();
  const [exam, setExam] = useState<ExamDetail | null>(null);
  const [results, setResults] = useState<Result[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const load = () => {
    setLoading(true);
    Promise.all([
      apiFetch<ExamDetail>(`/exams/${examId}`),
      apiFetch<Result[]>(`/exams/${examId}/results`),
    ])
      .then(([examRes, resultsRes]) => {
        if (examRes.success && examRes.data) setExam(examRes.data);
        if (resultsRes.success && Array.isArray(resultsRes.data)) setResults(resultsRes.data);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, [examId]);

  const togglePublish = async () => {
    if (!exam) return;
    setSaving(true);
    await apiFetch(`/exams/${examId}`, {
      method: "PATCH",
      body: JSON.stringify({ is_published: !exam.is_published }),
    });
    setSaving(false);
    load();
  };

  const removeExam = async () => {
    if (!exam || !window.confirm(t("deleteConfirm", { name: exam.title }))) return;
    const res = await apiFetch(`/exams/${examId}`, { method: "DELETE" });
    if (res.success) window.location.href = "/dashboard/exams";
  };

  if (loading) {
    return (
      <PageSection>
        <PageSkeleton />
      </PageSection>
    );
  }

  if (!exam) {
    return (
      <PageSection>
        <EmptyState title={t("notFound")} />
      </PageSection>
    );
  }

  return (
    <PageSection>
      <PageHeader
        title={exam.title}
        description={
          exam.description
            ? `${exam.description} · ${t("passScore")}: ${exam.pass_score}% · ${exam.duration_minutes} min`
            : `${t("passScore")}: ${exam.pass_score}% · ${exam.duration_minutes} min`
        }
        actions={
          <div className="flex gap-2 items-center flex-wrap">
            <Link href="/dashboard/exams">
              <Button variant="outline" size="sm">
                ← {t("back")}
              </Button>
            </Link>
            <PermissionGate permission="exams.update">
              <Button onClick={togglePublish} disabled={saving} loading={saving}>
                {exam.is_published ? t("unpublish") : t("publish")}
              </Button>
            </PermissionGate>
            {can("exams.delete") && (
              <Button variant="outline" className="text-danger border-danger/30 hover:bg-danger-bg" onClick={removeExam}>
                {t("delete")}
              </Button>
            )}
          </div>
        }
      />

      <Badge variant={exam.is_published ? "success" : "default"}>
        {exam.is_published ? t("published") : t("draft")}
      </Badge>

      <Card>
        <CardBody className="space-y-3">
          <CardTitle>{t("reviewQuestions")}</CardTitle>
          {exam.questions.map((q, idx) => (
            <div key={q.id} className="border border-border rounded-lg p-3 text-small">
              <p className="font-medium">
                {idx + 1}. {q.question_text}
              </p>
              <ul className="mt-2 space-y-1 text-muted-foreground">
                {(q.options_json || []).map((opt) => (
                  <li key={opt} className={opt === q.correct_answer ? "text-success font-medium" : ""}>
                    {opt}
                    {opt === q.correct_answer ? ` (${t("correct")})` : ""}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </CardBody>
      </Card>

      <Card>
        <CardBody>
          <CardTitle className="mb-3">{t("results")}</CardTitle>
          {results.length === 0 ? (
            <p className="text-small text-muted-foreground">{t("noResults")}</p>
          ) : (
            <ul className="space-y-2 text-small">
              {results.map((r) => (
                <li key={r.id} className="flex justify-between border-b border-border pb-1">
                  <span>{r.student_id.slice(0, 8)}…</span>
                  <span>
                    {r.score}/{r.max_score}{" "}
                    <Badge variant={r.passed ? "success" : "danger"}>{r.passed ? "✓" : "✗"}</Badge>
                  </span>
                </li>
              ))}
            </ul>
          )}
        </CardBody>
      </Card>
    </PageSection>
  );
}
