"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { PermissionGate } from "@/components/PermissionGate";
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

  if (loading) return <p className="text-gray-400">{t("loading")}</p>;
  if (!exam) return <p className="text-red-600">{t("notFound")}</p>;

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-start gap-4 flex-wrap">
        <div>
          <Link href="/dashboard/exams" className="text-sm text-naqsh-accent hover:underline">
            ← {t("back")}
          </Link>
          <h2 className="text-xl font-bold text-naqsh-primary mt-1">{exam.title}</h2>
          {exam.description && <p className="text-sm text-gray-500">{exam.description}</p>}
          <p className="text-sm text-gray-500 mt-1">
            {t("passScore")}: {exam.pass_score}% · {exam.duration_minutes} min
          </p>
        </div>
        <div className="flex gap-2">
          <PermissionGate permission="exams.update">
            <button
              type="button"
              disabled={saving}
              onClick={togglePublish}
              className="px-4 py-2 bg-naqsh-primary text-white rounded-lg text-sm disabled:opacity-50"
            >
              {exam.is_published ? t("unpublish") : t("publish")}
            </button>
          </PermissionGate>
          {can("exams.delete") && (
            <button type="button" onClick={removeExam} className="px-4 py-2 border border-red-300 text-red-600 rounded-lg text-sm">
              {t("delete")}
            </button>
          )}
        </div>
      </div>

      <section className="bg-white border rounded-xl p-4 space-y-3">
        <h3 className="font-semibold text-naqsh-primary">{t("reviewQuestions")}</h3>
        {exam.questions.map((q, idx) => (
          <div key={q.id} className="border rounded-lg p-3 text-sm">
            <p className="font-medium">
              {idx + 1}. {q.question_text}
            </p>
            <ul className="mt-2 space-y-1 text-gray-600">
              {(q.options_json || []).map((opt) => (
                <li key={opt} className={opt === q.correct_answer ? "text-green-700 font-medium" : ""}>
                  {opt}
                  {opt === q.correct_answer ? ` (${t("correct")})` : ""}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </section>

      <section className="bg-white border rounded-xl p-4">
        <h3 className="font-semibold text-naqsh-primary mb-2">{t("results")}</h3>
        {results.length === 0 ? (
          <p className="text-sm text-gray-400">{t("noResults")}</p>
        ) : (
          <ul className="space-y-2 text-sm">
            {results.map((r) => (
              <li key={r.id} className="flex justify-between border-b pb-1">
                <span>{r.student_id.slice(0, 8)}…</span>
                <span>
                  {r.score}/{r.max_score} {r.passed ? "✓" : "✗"}
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
