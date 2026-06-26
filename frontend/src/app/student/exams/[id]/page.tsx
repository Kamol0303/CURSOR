"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { apiFetch } from "@/lib/api";

type Question = {
  id: string;
  question_text: string;
  options_json: string[] | null;
};

type ExamDetail = {
  id: string;
  title: string;
  pass_score: number;
  duration_minutes: number;
  questions: Question[];
};

export default function StudentTakeExamPage() {
  const t = useTranslations("studentCabinet");
  const params = useParams();
  const router = useRouter();
  const examId = params.id as string;
  const [exam, setExam] = useState<ExamDetail | null>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<{ score: number; max_score: number; passed: boolean } | null>(null);

  useEffect(() => {
    apiFetch<ExamDetail>(`/exams/${examId}`)
      .then((res) => {
        if (res.success && res.data) setExam(res.data);
      })
      .finally(() => setLoading(false));
  }, [examId]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!exam) return;
    setSubmitting(true);
    const res = await apiFetch<{ score: number; max_score: number; passed: boolean }>(`/exams/${examId}/submit`, {
      method: "POST",
      body: JSON.stringify({
        answers: exam.questions.map((q) => ({
          question_id: q.id,
          answer: answers[q.id] || "",
        })),
      }),
    });
    setSubmitting(false);
    if (res.success && res.data) {
      setResult(res.data);
    }
  };

  if (loading) return <p className="text-gray-500 p-4">{t("loading")}</p>;
  if (!exam) return <p className="text-red-600 p-4">{t("examNotFound")}</p>;

  if (result) {
    return (
      <div className="min-h-screen bg-gray-50 p-4 max-w-lg mx-auto">
        <div className="bg-white rounded-xl border p-6 space-y-3 text-center">
          <h2 className="text-lg font-bold text-naqsh-primary">{t("examSubmitted")}</h2>
          <p className="text-2xl font-semibold">
            {result.score}/{result.max_score}
          </p>
          <p className={result.passed ? "text-green-700" : "text-red-600"}>
            {result.passed ? t("passed") : t("failed")}
          </p>
          <button
            type="button"
            onClick={() => router.push("/student/dashboard")}
            className="mt-4 px-4 py-2 bg-naqsh-primary text-white rounded-lg text-sm"
          >
            {t("backToDashboard")}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-naqsh-primary text-white px-4 py-4">
        <Link href="/student/dashboard" className="text-sm underline">
          ← {t("back")}
        </Link>
        <h1 className="font-bold text-lg mt-1">{exam.title}</h1>
        <p className="text-xs text-white/70">
          {t("passScore")}: {exam.pass_score}% · {exam.duration_minutes} min
        </p>
      </header>
      <form onSubmit={submit} className="p-4 max-w-lg mx-auto space-y-4">
        {exam.questions.map((q, idx) => (
          <div key={q.id} className="bg-white border rounded-xl p-4">
            <p className="font-medium text-sm mb-3">
              {idx + 1}. {q.question_text}
            </p>
            <div className="space-y-2">
              {(q.options_json || []).map((opt) => (
                <label key={opt} className="flex items-center gap-2 text-sm">
                  <input
                    type="radio"
                    name={q.id}
                    value={opt}
                    checked={answers[q.id] === opt}
                    onChange={() => setAnswers((prev) => ({ ...prev, [q.id]: opt }))}
                    required
                  />
                  {opt}
                </label>
              ))}
            </div>
          </div>
        ))}
        <button
          type="submit"
          disabled={submitting}
          className="w-full py-3 bg-naqsh-primary text-white rounded-lg font-medium disabled:opacity-50"
        >
          {submitting ? t("submitting") : t("submitExam")}
        </button>
      </form>
    </div>
  );
}
